import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

class authrequest:
    def __init__(self):
        self.youtube:googleapiclient.discovery.Resource=None
        self.api_service_name = "youtube"
        self.api_version = "v3"

        default_path = "../client_secret.json"
        fallback_path = "client_secret.json"
        if os.path.exists(default_path):
            self.client_secrets_file = default_path
        elif os.path.exists(fallback_path):
            self.client_secrets_file = fallback_path
        else:
            raise FileNotFoundError("client_secret.json not found in either ../ or current directory.")

    def makeAuthRequest(self)->bool:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, scopes)
        try:
            credentials = flow.run_local_server(timeout_seconds=20)
        except:
            return False
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials
        )
        return True
