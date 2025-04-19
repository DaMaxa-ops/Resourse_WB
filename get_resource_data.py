import requests
import json
import csv

INDICATORS = {
    "1": ("EG.USE.PCAP.KG.OE", "Энергопотребление на душу населения"),
    "2": ("ER.H2O.FWAG.ZS", "Использование воды в сельском хозяйстве (% от общего)"),
    "3": ("AG.LND.ARBL.ZS", "Пашня (% от общей площади)"),
    "4": ("EG.USE.COMM.GD.PP.KD", "Энергопотребление на $1000 ВВП (в эквиваленте нефти)")
}

def get_indicator_data():
    print("Выберите метрику:\n")
    for key, (code, desc) in INDICATORS.items():
        print(f"{key}: {desc} [{code}]")

    metric_choice = input("\nВведите номер метрики: ").strip()
    indicator_code, indicator_name = INDICATORS.get(metric_choice, (None, None))

    country_code = input("Введите код страны (например, US, RU, CN): ").upper()
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=1000"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if len(data) > 1 and isinstance(data[1], list):
            valid_data = [item for item in data[1] if item.get('value') is not None]

            latest = valid_data[0]
            latest_year = int(latest['date'])

            print(f"\n✅ Последний доступный год: {latest_year}")

            records = []
            for item in valid_data:
                if int(item['date']) == latest_year:
                    record = {
                        "country": country_code,
                        "year": item['date'],
                        "indicator": indicator_name,
                        "value": item['value'],
                        "unit": "см. описание метрики"
                    }
                    records.append(record)

            if records:
                for record in records:
                    print(record)

                filename = f"{country_code}_{indicator_code}_{latest_year}.csv"
                with open(filename, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

                print(f"Данные сохранены в файл: {filename}")

get_indicator_data()

