import base64
import hashlib
import hmac
import secrets
import string

import requests


HMAC_KEY = b"0123456789"


class FlyboxClient:
    def __init__(self, host, username, password):
        self.base_url = f"http://{host}"
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.csrf_token = None
        self.headers = {}

    def _hmac_md5_hex(self, value):
        return hmac.new(
            HMAC_KEY,
            value.encode("utf-8"),
            hashlib.md5
        ).hexdigest()

    def _random_nonce(self, length=24):
        chars = string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    def _xor_bytes(self, a, b):
        return bytes(x ^ y for x, y in zip(a, b))

    def _parse_scram_server_first(self, response):
        result = {}

        for part in response.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                result[key] = value

        return result

    def _update_csrf(self, response):
        token = response.headers.get("X-Csrf-Token")

        if token:
            self.csrf_token = token
            self.headers["X-Csrf-Token"] = token

    def _get_csrf_token(self):
        response = self.session.get(
            self.base_url + "/goform/x_csrf_token",
            params={"v": secrets.randbelow(10**12)},
            timeout=10,
        )
        response.raise_for_status()

        token = response.headers.get("X-Csrf-Token")

        if not token:
            raise RuntimeError(
                "Flybox nevrátil X-Csrf-Token."
            )

        self.csrf_token = token

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "X-Csrf-Token": token,
            "Origin": self.base_url,
            "Referer": self.base_url + "/",
        }

    def login(self):
        self._get_csrf_token()

        hmac_username = self._hmac_md5_hex(
            self.username
        )
        hmac_password = self._hmac_md5_hex(
            self.password
        )

        nonce = self._random_nonce(24)

        client_first_bare = (
            f"n={hmac_username},r={nonce}"
        )

        payload = {
            "username": hmac_username,
            "password": "n,," + client_first_bare,
        }

        response = self.session.post(
            self.base_url + "/goform/scram_first_message",
            headers=self.headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        self._update_csrf(response)

        data = response.json()

        if str(data.get("retcode")) != "0":
            raise RuntimeError(
                f"SCRAM first message zlyhal: {data}"
            )

        server_first = data["response"]

        values = self._parse_scram_server_first(
            server_first
        )

        final_nonce = values["r"]
        salt_string = values["s"]
        iterations = int(values["i"])

        salted_password = hashlib.pbkdf2_hmac(
            "sha256",
            hmac_password.encode("utf-8"),
            salt_string.encode("utf-8"),
            iterations,
            dklen=32,
        )

        client_key = hmac.new(
            salted_password,
            b"Client Key",
            hashlib.sha256,
        ).digest()

        stored_key = hashlib.sha256(
            client_key
        ).digest()

        client_final_without_proof = (
            f"c=biws,r={final_nonce}"
        )

        auth_message = (
            client_first_bare
            + ","
            + server_first
            + ","
            + client_final_without_proof
        )

        client_signature = hmac.new(
            stored_key,
            auth_message.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        client_proof = self._xor_bytes(
            client_key,
            client_signature
        )

        proof_b64 = base64.b64encode(
            client_proof
        ).decode("ascii")

        login_payload = {
            "username": hmac_username,
            "password": (
                f"{client_final_without_proof},"
                f"p={proof_b64}"
            ),
        }

        response = self.session.post(
            self.base_url + "/goform/login",
            headers=self.headers,
            json=login_payload,
            timeout=10,
        )
        response.raise_for_status()

        self._update_csrf(response)

        data = response.json()

        if str(data.get("retcode")) != "0":
            raise RuntimeError(
                f"Flybox login zlyhal: {data}"
            )

        return True

    def get_params(self, keys):
        payload = {
            "keys": keys
        }

        try:
            response = self.session.post(
                self.base_url + "/goform/get_mgdb_params",
                headers=self.headers,
                json=payload,
                timeout=10,
            )

            if response.status_code == 403:
                self.login()

                response = self.session.post(
                    self.base_url + "/goform/get_mgdb_params",
                    headers=self.headers,
                    json=payload,
                    timeout=10,
                )

            response.raise_for_status()

            self._update_csrf(response)

            data = response.json()

            if str(data.get("retcode")) != "0":
                raise RuntimeError(
                    f"Flybox get_params zlyhal: {data}"
                )

            return data.get("data", {})

        except requests.RequestException:
            self.login()

            response = self.session.post(
                self.base_url + "/goform/get_mgdb_params",
                headers=self.headers,
                json=payload,
                timeout=10,
            )

            response.raise_for_status()

            self._update_csrf(response)

            data = response.json()

            if str(data.get("retcode")) != "0":
                raise RuntimeError(
                    f"Flybox get_params zlyhal: {data}"
                )

            return data.get("data", {})


    def get_hosts(self):
        try:
            response = self.session.post(
                self.base_url + "/action/router_get_hosts_info",
                headers=self.headers,
                json={},
                timeout=10,
            )

            if response.status_code == 403:
                self.login()
                response = self.session.post(
                    self.base_url + "/action/router_get_hosts_info",
                    headers=self.headers,
                    json={},
                    timeout=10,
                )

            response.raise_for_status()
            self._update_csrf(response)

            data = response.json()

            if str(data.get("retcode")) != "0":
                raise RuntimeError(f"Flybox get_hosts zlyhal: {data}")

            return data.get("data", {})

        except requests.RequestException:
            self.login()

            response = self.session.post(
                self.base_url + "/goform/router_get_hosts_info",
                headers=self.headers,
                timeout=10,
            )

            response.raise_for_status()
            self._update_csrf(response)

            data = response.json()

            if str(data.get("retcode")) != "0":
                raise RuntimeError(f"Flybox get_hosts zlyhal: {data}")

            return data.get("data", {})

    def set_wifi_state(self, key, enabled):
        value = "ap_enable" if enabled else "ap_disable"

        payload = {
            key: value,
        }

        response = self.session.post(
            self.base_url + "/action/wifi_set_basic_params",
            json=payload,
            headers=self.headers,
            timeout=10,
        )

        if response.status_code == 403:
            self.login()
            response = self.session.post(
                self.base_url + "/action/wifi_set_basic_params",
                json=payload,
                headers=self.headers,
                timeout=10,
            )

        response.raise_for_status()
        self._update_csrf(response)

        data = response.json()

        if str(data.get("retcode")) != "0":
            raise RuntimeError(
                f"Flybox set_wifi_state zlyhal: {data}"
            )

        return data
