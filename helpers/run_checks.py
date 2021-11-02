import json
import secrets

from .copyleaks import Copyleaks, Products


def process_checks(repo, urls, auth_token, host):

    PRODUCT = Products.EDUCATION

    parent_id = secrets.token_hex(16)

    submission = {"properties":
                {"webhooks": {},
                 "author": {
                     "id": repo
                 },
                 "developerPayload": f"{repo}:{parent_id}",
                 "sensitivityLevel": 5,
                 "scanning": 
                    {"internet": True,
                     "copyleaksDb": 
                        {"includeMySubmissions": True,
                         "includeOthersSubmissions": True
                        }
                    }
                }
              }

    for url in urls:

        scan_id = secrets.token_hex(16)

        submission["url"] = url

        submission["properties"]["webhooks"]["status"] = f"https://{host}/scans/{scan_id}"

        Copyleaks.submit_url(PRODUCT, auth_token, scan_id, submission)
    
    return parent_id