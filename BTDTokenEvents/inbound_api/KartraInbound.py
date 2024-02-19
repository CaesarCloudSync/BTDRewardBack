import json
import subprocess
class KartraInbound:
    def __init__(self) -> None:
        # PHP Samples
        # https://documentation.kartra.com/category/api/api-inbound/api-inbound-php-samples/
        self.inbound_dir = "inbound_api"
    def get_lead_details(self,email):
        with open(f"{self.inbound_dir}/get_leads_read.php","r") as f:
            get_email_read = f.read()
        get_email_read = get_email_read.replace(r"{{email}}",email)

        with open(f"{self.inbound_dir}/get_leads_write.php","w+") as f:
            f.write(get_email_read)
        proc = subprocess.Popen(f"php {self.inbound_dir}/get_leads_write.php", shell=True, stdout=subprocess.PIPE)
        script_response = proc.stdout.read()
        json_data = json.loads(script_response.decode())
        if json_data["status"] == "Error":
            return json_data
        else:
            lead_details = json_data["lead_details"]
            return lead_details
if __name__ == "__main__":
    kartrainbound = KartraInbound()
    value = kartrainbound.get_lead_details("amari.lawal@gmail.com")
    print(value)