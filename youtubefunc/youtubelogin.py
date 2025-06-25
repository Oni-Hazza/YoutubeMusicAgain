import os

import google_auth_oauthlib.flow
import google_auth_oauthlib.helpers
import googleapiclient.discovery
import googleapiclient.errors
import json



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
    
    def authenticate(self, cache_file)->bool:
        if self.loadFromExisting(cache_file):
            return True
        elif self.makeAuthRequest(cache_file):
            return True
        else:
            return False

    def makeAuthRequest(self, cache_file)->bool:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, scopes)
        try:
            credentials = flow.run_local_server(timeout_seconds=20)
            
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(credentials.to_json())
        except:
            return False
        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials,
        )
        return True
    
    def loadFromExisting(self, cache_file)->bool:
        try:
            if cache_file.exists():
                with open(cache_file, "r") as f:
                    data = f.read()
                    jsn = json.loads(data)
            else:
                return False
            
            test = google_auth_oauthlib.flow.google_auth_oauthlib.helpers.external_account_authorized_user.Credentials(
                token=jsn["token"],
                #expiry=jsn["expiry"],
                refresh_token=jsn["refresh_token"],
                client_id=jsn["client_id"],
                client_secret=jsn["client_secret"],
                token_url=jsn["token_uri"],
                scopes=jsn["scopes"],
                universe_domain=jsn["universe_domain"]                
                )
            self.youtube = googleapiclient.discovery.build(self.api_service_name, self.api_version, credentials=test)
            return True
        except Exception as e:
            print(e)
            return False
