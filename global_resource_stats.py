import requests
import csv
import time

INDICATORS = {
    "EG.USE.PCAP.KG.OE": "Энергопотребление на душу населения",
    "ER.H2O.FWAG.ZS": "Использование воды в сельском хозяйстве (% от общего)",
    "AG.LND.ARBL.ZS": "Пашня (% от общей площади)",
    "EG.USE.COMM.GD.PP.KD": "Энергопотребление на $1000 ВВП (в эквиваленте нефти)"
}

def get_all_country_codes():
    url = "http://api.worldbank.org/v2/country?format=json&per_page=400"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            return [country['id'] for country in data[1] if country['region']['value'] != "Aggregates"]
    return []

def get_latest_data_for_indicator(indicator_code, indicator_name):
    country_codes = get_all_country_codes()
    records = []

    for i, country in enumerate(country_codes):
        url = f"http://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}?format=json&per_page=1000"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                valid = [item for item in data[1] if item.get('value') is not None]
                if valid:
                    latest = valid[0]
                    record = {
                        "country": country,
                        "year": latest['date'],
                        "indicator": indicator_name,
                        "value": latest['value'],
                        "unit": "см. описание метрики"
                    }
                    records.append(record)
        time.sleep(0.1)

    return records

def save_to_csv(indicator_code, indicator_name, records):
    if records:
        filename = f"{indicator_code}_latest.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        print(f"Сохранено: {filename}")

def main():
    for code, name in INDICATORS.items():
        data = get_latest_data_for_indicator(code, name)
        save_to_csv(code, name, data)

main()
