import requests
import json


def get_location(ip: str) -> dict:
	url = "http://ipinfo.io/{0}".format(ip)
	r = requests.get(url)
	html = json.loads(r.text)

	try:
		information = {
			"Country": html['country'],
			"IP": html['ip'],
			"City": html['city'],
			"Region": html['region'],
			"TimeZone": html['timezone'],
			"Loc": html['loc']
		}
	except KeyError:
		information = {}

	return information


