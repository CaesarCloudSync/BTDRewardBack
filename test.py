import subprocess
import json
# if the script don't need output.
#subprocess.call("php get_leads_write.php")
email = "maintestkartra@kartra.com"
with open("get_leads_read.php","r") as f:
    get_email_read = f.read()
get_email_read = get_email_read.replace(r"{{email}}",email)

with open("get_leads_write.php","w+") as f:
    f.write(get_email_read)
    
# if you want output
proc = subprocess.Popen("php get_leads_write.php", shell=True, stdout=subprocess.PIPE)
script_response = proc.stdout.read()
json_data = json.loads(script_response.decode())
if json_data["status"] == "Error":
    print(json_data)
else:
    lead_details = json_data["lead_details"]
    print(lead_details)