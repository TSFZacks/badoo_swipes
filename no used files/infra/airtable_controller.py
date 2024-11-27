
from airtable import Airtable



class AirtableController:
    def __init__(self, _base_key, _table_name, _api_key):
        
        self._base_key = _base_key
        self._table_name = _table_name
        self._api_key = _api_key
        self._airtable = Airtable(_base_key, _table_name,api_key=_api_key)
    
    def get_all(self):
        self._airtable.get_all()
        
    def save(self, data):
        try:
            self._airtable.insert(data)
        except Exception as e:
            print(e)
            
    def save_account_google(self, email, password, username, modelName):
        data = {
            "Name": username,
            "Email": email,
            "Model Name": modelName,
            "Password": password
        }
        self.save(data)
    def save_profile(self, dolphin_name, dolphin_id, model_name, proxy_name):
        data = {
            "Model Name": model_name,
            "Dolphin Name": model_name,
            "Dolphin ID": dolphin_id,
            "Proxy Name": proxy_name,
            "Tags":["Laurie", "UK", "Badoo"],
            "Status":["Stage 1"],
        }
        self.save(data)
            
# _base_key = 'app4qWZiEHjN9gCA4'
# _table_name = 'Profiles copy'
# _api_key = 'patrxYIXclUNRsznA.80f3f4ebfa2cb21012c25b71c90bc211e75c38c005841b3826c5fcf1ffbe843f'
# airtable_email = AirtableController(_base_key, _table_name, _api_key)
# airtable_email.save_profile("nome", 1231313, "test", "tst")
# print(airtable_email.get_all())


