import sys
import re
from collections import defaultdict

def parse_input(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Split sections
        sections = re.split(r'\[Stations\]|\[Charger Availability Reports\]', content)
        if len(sections) < 3:
            raise ValueError("Missing sections in input file.")

        stations_data = sections[1].strip()
        availability_data = sections[2].strip()

        # Parse stations
        stations = {}
        for line in stations_data.splitlines():
            parts = line.split()
            if len(parts) < 2:
                raise ValueError("Invalid station entry.")
            station_id = int(parts[0])
            charger_ids = list(map(int, parts[1:]))
            stations[station_id] = charger_ids

        # Parse charger availability
        charger_availability = defaultdict(list)
        for line in availability_data.splitlines():
            parts = line.split()
            if len(parts) != 4:
                raise ValueError("Invalid availability report entry.")
            charger_id = int(parts[0])
            start_time = int(parts[1])
            end_time = int(parts[2])
            up = parts[3].lower() == 'true'
            charger_availability[charger_id].append((start_time, end_time, up))

        return stations, charger_availability

    except Exception as e:
        print("ERROR", file=sys.stdout)
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)

def calculate_uptime(stations, charger_availability):
    station_uptime = {}

    for station_id, charger_ids in stations.items():
        total_time = 0
        up_time = 0

        for charger_id in charger_ids:
            if charger_id not in charger_availability:
                continue

            reports = charger_availability[charger_id]
            reports.sort()  # Sort by start time

            last_end_time = None
            for start_time, end_time, up in reports:
                if last_end_time is not None and start_time > last_end_time:
                    total_time += start_time - last_end_time

                total_time += end_time - start_time
                if up:
                    up_time += end_time - start_time

                last_end_time = max(last_end_time or 0, end_time)

        if total_time > 0:
            station_uptime[station_id] = (up_time * 100) // total_time
        else:
            station_uptime[station_id] = 0

    return station_uptime

def main():
    if len(sys.argv) != 2:
        print("ERROR", file=sys.stdout)
        sys.stderr.write("Usage: python station_uptime.py <input_file>\n")
        sys.exit(1)

    file_path = sys.argv[1]
    stations, charger_availability = parse_input(file_path)
    station_uptime = calculate_uptime(stations, charger_availability)

    for station_id in sorted(station_uptime.keys()):
        print(f"{station_id} {station_uptime[station_id]}")

if __name__ == "__main__":
    main()
