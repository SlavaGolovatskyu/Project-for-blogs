import requests
import json


def get_location(ip: str) -> dict:
	url = "http://ipinfo.io/{0}?token=94ef890b6142e2".format(ip)
	r = requests.get(url)
	html = json.loads(r.text)

	try:
		return {
			"Country": html['country'],
			"IP": html['ip'],
			"City": html['city'],
			"Region": html['region'],
			"TimeZone": html['timezone'],
			"Loc": html['loc']
		}
	except KeyError:
		return {}


