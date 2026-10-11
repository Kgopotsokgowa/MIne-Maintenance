# MINING MONITORING SYSTEM
# Rewritten using only the concepts covered in MINN2020A:
# variables, if/elif/else, while and for loops, functions, lists, tuples,
# dictionaries, sets and string methods.

from datetime import datetime
import time

# ----------------------------------------------------------------------
# DATA STORAGE (lists, a set and constants)
# ----------------------------------------------------------------------
workers = []
incidents = []
equipment_records = []
maintenance_records = []
risk_records = []
alert_log = []
alert_keys = set()          # remembers alerts already raised (no duplicates)

positions = ["Administrator", "Safety Officer", "Mining Engineer", "Maintenance Engineer", "Manager"]

functions = ["View Dashboard", "Worker Safety Data", "Safety Incidents", "Equipment Data",
             "Maintenance Data", "Risk Assessment", "Generate Reports", "Manage Users"]

permissions = {
    "Administrator": ["View Dashboard", "Worker Safety Data", "Safety Incidents", "Equipment Data",
                      "Maintenance Data", "Risk Assessment", "Generate Reports", "Manage Users"],
    "Safety Officer": ["View Dashboard", "Worker Safety Data", "Safety Incidents",
                       "Risk Assessment", "Generate Reports"],
    "Mining Engineer": ["View Dashboard", "Worker Safety Data", "Safety Incidents", "Equipment Data",
                        "Maintenance Data", "Risk Assessment", "Generate Reports"],
    "Maintenance Engineer": ["View Dashboard", "Equipment Data", "Maintenance Data", "Generate Reports"],
    "Manager": ["View Dashboard", "Worker Safety Data", "Safety Incidents", "Equipment Data",
                "Maintenance Data", "Risk Assessment", "Generate Reports"]
}

equipment_types = ["Haul Trucks", "Loaders", "Excavators", "Drilling Machines",
                   "Bulldozers", "Scraper Winches", "Crushers", "Conveyors"]

# Monitoring limits
TEMP_WARN = 80
TEMP_CRIT = 100
VIB_WARN = 5
VIB_CRIT = 8
DOWNTIME_LIMIT = 10
ALERT_LIMIT = 3
AVAILABILITY_LIMIT = 80


# ----------------------------------------------------------------------
# INPUT HELPER FUNCTIONS
# ----------------------------------------------------------------------
def is_whole_number(text):
    # A whole number may start with a minus sign, the rest must be digits
    if text.startswith("-"):
        text = text[1:]
    return text.isdigit()


def is_number(text):
    # A number may start with a minus sign and contain one decimal point
    if text.startswith("-"):
        text = text[1:]
    if text.count(".") > 1:
        return False
    text = text.replace(".", "")
    return text.isdigit()


def is_valid_date(text):
    # Checks the format YYYY-MM-DD and that the date really exists
    parts = text.split("-")
    if len(parts) != 3:
        return False
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return False
    if not (parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit()):
        return False

    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    if year < 1 or month < 1 or month > 12:
        return False

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_month[1] = 29      # leap year

    return day >= 1 and day <= days_in_month[month - 1]


def is_valid_time(text):
    # Checks the format HH:MM
    parts = text.split(":")
    if len(parts) != 2:
        return False
    if len(parts[0]) < 1 or len(parts[0]) > 2 or len(parts[1]) < 1 or len(parts[1]) > 2:
        return False
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return False
    return int(parts[0]) <= 23 and int(parts[1]) <= 59


def get_text(prompt):
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("Input cannot be empty.")


def get_int(prompt, low, high):
    # high = None means there is no upper limit
    while True:
        text = input(prompt).strip()
        if not is_whole_number(text):
            print("Invalid input: enter a whole number.")
        else:
            value = int(text)
            if value < low or (high is not None and value > high):
                print("Value out of range.")
            else:
                return value


def get_float(prompt, low):
    while True:
        text = input(prompt).strip()
        if not is_number(text):
            print("Invalid input: enter a number.")
        else:
            value = float(text)
            if value < low:
                print("Value must be at least", low)
            else:
                return value


def get_choice(prompt, options):
    while True:
        value = input(f"{prompt} ({'/'.join(options)}): ").strip().lower()
        for option in options:
            if value == option.lower():
                return option
        print("Invalid choice, try again.")


def get_date(prompt):
    while True:
        value = input(prompt + " (YYYY-MM-DD): ").strip()
        if is_valid_date(value):
            return value
        print("Invalid date format.")


def get_time(prompt):
    while True:
        value = input(prompt + " (HH:MM): ").strip()
        if is_valid_time(value):
            return value
        print("Invalid time format.")


# ----------------------------------------------------------------------
# LOGIN AND PERMISSIONS
# ----------------------------------------------------------------------
def validate_position(entered):
    for p in positions:
        if entered.strip().lower() == p.lower():
            return p
    return None


def get_permissions(position):
    return permissions[position]


def display_permissions(position):
    print(f"Access granted for {position}. Functions accessible:")
    for func in get_permissions(position):
        print("-", func)


def login():
    print("Positions:", ", ".join(positions))
    while True:
        entered = input("Enter your work position (or 'exit'): ")
        if entered.strip().lower() == "exit":
            return None
        position = validate_position(entered)
        if position is not None:
            display_permissions(position)
            return position
        print("Access Denied, Enter Valid Position")


# ----------------------------------------------------------------------
# WORKER SAFETY
# ----------------------------------------------------------------------
def get_worker_info():
    worker_info = {}
    worker_info['Worker ID'] = get_text("Enter Worker ID: ").upper()
    worker_info['Department'] = get_text("Enter Department: ")
    worker_info['Job Role'] = get_text("Enter Job Role: ")
    worker_info['Shift'] = get_choice("Enter Shift", ["Day", "Night"])
    worker_info['PPE Compliance'] = get_choice("PPE Compliance", ["Yes", "No"])
    worker_info['Safety Training Status'] = get_choice("Safety Training Status", ["Yes", "No"])
    worker_info['Fatigue Level'] = get_choice("Fatigue Level", ["Low", "Medium", "High"])
    worker_info['Safety Observations'] = get_choice("Any unsafe safety observation?", ["Yes", "No"])
    worker_info['Near Misses'] = get_int("Number of Near Misses: ", 0, None)
    worker_info['Previous Incidents'] = get_int("Number of Previous Incidents: ", 0, None)
    return worker_info


def generate_warnings(worker_info):
    # Each warning is a tuple: (message, is_serious)
    warnings = []
    if worker_info['PPE Compliance'] == "No":
        warnings.append(("PPE Non-Compliance Detected", True))
    if worker_info['Safety Training Status'] == "No":
        warnings.append(("Training Required", False))
    if worker_info['Fatigue Level'] == "High":
        warnings.append(("Worker Fatigue Risk - Recommend Rest", True))
    if worker_info['Near Misses'] > 0:
        warnings.append(("Near Miss Reported - Review Required", False))
    if worker_info['Previous Incidents'] > 0:
        warnings.append(("Prior Incident on Record", False))
    if worker_info['Safety Observations'] == "Yes":
        warnings.append(("Unsafe Safety Observation Detected", True))
    return warnings


def determine_risk_level(warnings):
    serious_found = False
    for warning in warnings:
        if warning[1] == True:
            serious_found = True

    if serious_found:
        return "High"
    elif len(warnings) > 0:
        return "Medium"
    else:
        return "Low"


def store_worker(worker_info):
    # Replace the record if the worker already exists, otherwise add it
    for i in range(len(workers)):
        if workers[i]['Worker ID'] == worker_info['Worker ID']:
            workers[i] = worker_info
            return
    workers.append(worker_info)


def display_worker_result(risk_level, warnings):
    print("\nRisk Level:", risk_level)
    print("Warnings:")
    for warning in warnings:
        print("-", warning[0])
    if len(warnings) == 0:
        print("- None")


def worker_safety():
    worker_info = get_worker_info()
    warnings = generate_warnings(worker_info)
    risk_level = determine_risk_level(warnings)

    worker_info['Risk Level'] = risk_level
    messages = []
    for warning in warnings:
        messages.append(warning[0])
    worker_info['Warnings'] = messages

    store_worker(worker_info)
    display_worker_result(risk_level, warnings)


def view_workers():
    if len(workers) == 0:
        print("No worker records.")
    for w in workers:
        print(f"{w['Worker ID']:<8}{w['Department']:<14}{w['Shift']:<7}PPE:{w['PPE Compliance']:<4} Fatigue:{w['Fatigue Level']:<7} Risk:{w['Risk Level']}")


def worker_menu():
    while True:
        choice = get_choice("\nWorker Safety Data", ["Record", "View", "Back"])
        if choice == "Record":
            worker_safety()
        elif choice == "View":
            view_workers()
        else:
            return


# ----------------------------------------------------------------------
# SAFETY INCIDENTS
# ----------------------------------------------------------------------
def display_incidents(incidents_list):
    if len(incidents_list) == 0:
        print("No incidents found.")
        return
    for inc in incidents_list:
        print(inc)


def find_key(name, sample):
    # Finds the dictionary key that matches the typed name (ignoring case)
    for k in sample:
        if k.lower() == name.strip().lower():
            return k
    return None


def get_incident_info():
    incident = {}
    incident['Incident ID'] = len(incidents) + 1
    incident['Date'] = get_date("Enter Date")
    incident['Time'] = get_time("Enter Time")
    incident['Shift'] = get_choice("Enter Shift", ["Day", "Night"])
    incident['Location'] = get_text("Enter Location: ")
    incident['Department'] = get_text("Enter Department: ")
    incident['Incident Type'] = get_text("Enter Incident Type: ")
    incident['Severity'] = get_choice("Enter Severity", ["Low", "Medium", "High", "Critical"])
    incident['Injury Status'] = get_text("Enter Injury Status: ")
    incident['Lost-Time Injury Status'] = get_choice("Lost-Time Injury", ["Yes", "No"])
    incident['Cause'] = get_text("Enter Cause: ")
    incident['Corrective Action'] = get_text("Enter Corrective Action: ")
    incident['Incident Status'] = get_choice("Incident Status", ["Open", "Under Investigation", "Closed"])
    return incident


def add_incident():
    incident = get_incident_info()
    incidents.append(incident)
    print("Incident added.")


def view_incidents():
    display_incidents(incidents)


def search_incidents():
    term = get_text("Enter search term: ").lower()
    results = []
    for inc in incidents:
        if term in str(inc).lower():
            results.append(inc)
    display_incidents(results)


def filter_incidents():
    if len(incidents) == 0:
        print("No incidents recorded.")
        return
    key = find_key(input("Filter by (Date/Shift/Location/Department/Severity/Incident Type): "), incidents[0])
    if key is None:
        print("Invalid filter field.")
        return
    value = get_text(f"Enter {key}: ").lower()
    results = []
    for inc in incidents:
        if str(inc[key]).lower() == value:
            results.append(inc)
    display_incidents(results)


def categorize_incidents():
    if len(incidents) == 0:
        print("No incidents recorded.")
        return
    key = find_key(input("Categorize by (Incident Type/Severity/Department): "), incidents[0])
    if key is None:
        print("Invalid category.")
        return

    categorized = {}
    for inc in incidents:
        if inc[key] in categorized:
            categorized[inc[key]].append(inc)
        else:
            categorized[inc[key]] = [inc]

    for category in categorized:
        items = categorized[category]
        print(f"\nCategory: {category} ({len(items)})")
        display_incidents(items)


def count_incidents():
    print("Total incidents recorded:", len(incidents))


def count_by_field(field):
    counts = {}
    for inc in incidents:
        counts[inc[field]] = counts.get(inc[field], 0) + 1
    return counts


def sort_counts(counts):
    # Turns the dictionary into a list of (name, count) tuples
    # and sorts it from the largest count to the smallest (bubble sort)
    pairs = []
    for key in counts:
        pairs.append((key, counts[key]))

    for i in range(len(pairs)):
        for j in range(len(pairs) - 1 - i):
            if pairs[j][1] < pairs[j + 1][1]:
                temp = pairs[j]
                pairs[j] = pairs[j + 1]
                pairs[j + 1] = temp
    return pairs


def analyse_trends():
    if len(incidents) == 0:
        print("No incidents recorded.")
        return
    for field in ["Severity", "Shift", "Department", "Incident Type", "Cause"]:
        print(f"\nIncident Trends by {field}:")
        sorted_pairs = sort_counts(count_by_field(field))
        for pair in sorted_pairs:
            print(f"{pair[0]}: {pair[1]}")


def incident_menu():
    while True:
        print("\nOptions: Add Incident, View Incidents, Search Incidents, Filter Incidents, "
              "Categorize Incidents, Count Incidents, Analyse Trends, Back")
        choice = input("Choose an option: ").strip().lower()

        if choice == "back":
            return
        elif choice == "add incident":
            add_incident()
        elif choice == "view incidents":
            view_incidents()
        elif choice == "search incidents":
            search_incidents()
        elif choice == "filter incidents":
            filter_incidents()
        elif choice == "categorize incidents":
            categorize_incidents()
        elif choice == "count incidents":
            count_incidents()
        elif choice == "analyse trends":
            analyse_trends()
        else:
            print("Invalid option.")


# ----------------------------------------------------------------------
# EQUIPMENT DATA
# ----------------------------------------------------------------------
def calculate_availability(op_time, downtime):
    if op_time + downtime == 0:
        return 0
    return round((op_time / (op_time + downtime)) * 100, 2)


def get_equipment_info():
    print("Equipment types:", ", ".join(equipment_types))
    eq = {}
    eq['Equipment Type'] = get_choice("Equipment Type", equipment_types)
    eq['Equipment ID'] = len(equipment_records) + 1
    eq['Manufacturer'] = get_text("Manufacturer: ")
    eq['Operating Hours'] = get_float("Operating Hours: ", 0.0)
    eq['Temperature'] = get_float("Temperature (C): ", -50)
    eq['Vibration'] = get_float("Vibration (mm/s): ", 0.0)
    eq['Fuel Consumption'] = get_float("Fuel Consumption (L/h): ", 0.0)
    eq['Brake Status'] = get_choice("Brake Status", ["Good", "Worn", "Faulty"])
    eq['Tyre Status'] = get_choice("Tyre Status", ["Good", "Worn", "Faulty"])
    eq['Engine Status'] = get_choice("Engine Status", ["Good", "Fair", "Faulty"])
    eq['Maintenance Status'] = get_choice("Maintenance Status", ["Not Started", "In Progress", "Completed"])
    eq['Downtime'] = get_float("Downtime (hours): ", 0.0)
    eq['Availability'] = calculate_availability(eq['Operating Hours'], eq['Downtime'])
    eq['Scheduled Maintenance Date'] = get_date("Scheduled Maintenance Date")
    eq['Number of Alerts'] = 0
    return eq


def add_equipment():
    eq = get_equipment_info()
    equipment_records.append(eq)
    print(f"Equipment added with ID {eq['Equipment ID']}. Availability = {eq['Availability']}%")


def view_equipment():
    if len(equipment_records) == 0:
        print("No equipment records.")
    for eq in equipment_records:
        print(eq)


def search_equipment():
    term = get_text("Enter search term: ")
    found = False
    for eq in equipment_records:
        if term.lower() in str(eq).lower():
            print(eq)
            found = True
    if not found:
        print("No matching equipment found.")


def filter_equipment():
    eq_type = get_text("Enter Equipment Type to filter: ")
    found = False
    for eq in equipment_records:
        if eq["Equipment Type"].lower() == eq_type.lower():
            print(eq)
            found = True
    if not found:
        print("No equipment found of that type.")


# ----------------------------------------------------------------------
# CONDITION MONITORING
# ----------------------------------------------------------------------
def temp_status(temp):
    if temp < TEMP_WARN:
        return "NORMAL"
    elif temp <= TEMP_CRIT:
        return "WARNING"
    else:
        return "CRITICAL"


def vib_status(vib):
    if vib < VIB_WARN:
        return "NORMAL"
    elif vib <= VIB_CRIT:
        return "WARNING"
    else:
        return "CRITICAL"


def get_condition_messages(t_stat, v_stat):
    messages = []
    if t_stat == "NORMAL" and v_stat == "NORMAL":
        messages.append("NORMAL: Equipment operating within defined monitoring limits.")
    if t_stat == "WARNING":
        messages.append("WARNING: Equipment temperature approaching predefined threshold.")
    if v_stat == "WARNING":
        messages.append("WARNING: Equipment vibration approaching predefined threshold.")
    if t_stat == "CRITICAL":
        messages.append("CRITICAL: Equipment temperature exceeds predefined threshold. Inspection required")
    if v_stat == "CRITICAL":
        messages.append("CRITICAL: Equipment vibration exceeds predefined threshold. Inspection required")
    return messages


def display_condition(eq, t_stat, v_stat):
    print(f"\nEquipment ID: {eq['Equipment ID']} ({eq['Equipment Type']}), "
          f"Temp: {eq['Temperature']} C [{t_stat}], Vibration: {eq['Vibration']} mm/s [{v_stat}]")
    for message in get_condition_messages(t_stat, v_stat):
        print(message)
    if t_stat == "CRITICAL" or v_stat == "CRITICAL":
        print(f"ALERT: Immediate attention required by Maintenance Engineer and Manager for Equipment ID {eq['Equipment ID']}")


def condition_monitoring():
    if len(equipment_records) == 0:
        print("No equipment recorded.")
        return
    for eq in equipment_records:
        t_stat = temp_status(eq["Temperature"])
        v_stat = vib_status(eq["Vibration"])
        eq["Temperature Status"] = t_stat
        eq["Vibration Status"] = v_stat
        display_condition(eq, t_stat, v_stat)


def equipment_menu():
    while True:
        print("\nOptions: Add Equipment, View Equipment, Search Equipment, Filter Equipment, "
              "Condition Monitoring, Back")
        choice = input("Choose an option: ").strip().lower()

        if choice == "back":
            return
        elif choice == "add equipment":
            add_equipment()
        elif choice == "view equipment":
            view_equipment()
        elif choice == "search equipment":
            search_equipment()
        elif choice == "filter equipment":
            filter_equipment()
        elif choice == "condition monitoring":
            condition_monitoring()
        else:
            print("Invalid option.")


# ----------------------------------------------------------------------
# MAINTENANCE DATA
# ----------------------------------------------------------------------
def get_maintenance_flags(eq):
    flags = []
    # Dates in the format YYYY-MM-DD can be compared as strings
    today = datetime.today().strftime("%Y-%m-%d")
    scheduled = eq["Scheduled Maintenance Date"]

    if scheduled == today:
        flags.append("Due for Maintenance")
    elif scheduled < today:
        flags.append("Overdue")
    if eq["Maintenance Status"].lower() == "in progress":
        flags.append("Under Maintenance")
    if eq["Downtime"] > DOWNTIME_LIMIT:
        flags.append("Excessive Downtime")
    if eq["Number of Alerts"] > ALERT_LIMIT:
        flags.append("Repeated Alerts")
    if eq["Availability"] < AVAILABILITY_LIMIT:
        flags.append("Low Availability")
    return flags


def find_equipment(eq_id):
    for eq in equipment_records:
        if eq["Equipment ID"] == eq_id:
            return eq
    return None


def get_maintenance_input(eq):
    data = {}
    data["Operating Hours"] = get_float("Operating Time (hours): ", 0.0)
    data["Downtime"] = get_float("Downtime (hours): ", 0.0)
    data["Scheduled Maintenance Date"] = get_date("Scheduled Maintenance Date")
    data["Maintenance Status"] = get_choice("Maintenance Status", ["Not Started", "In Progress", "Completed"])
    data["Number of Alerts"] = get_int("Number of Alerts: ", eq["Number of Alerts"], None)
    data["Availability"] = calculate_availability(data["Operating Hours"], data["Downtime"])
    return data


def display_maintenance_result(eq_id, availability, flags):
    print(f"Equipment {eq_id} Availability: {availability:.2f}%")
    if len(flags) > 0:
        print("Flags:", ", ".join(flags))
    else:
        print("Flags: None")


def update_maintenance():
    if len(equipment_records) == 0:
        print("No equipment recorded. Add equipment first.")
        return
    eq_id = get_int("Enter Equipment ID: ", 1, None)
    eq = find_equipment(eq_id)
    if eq is None:
        print("Equipment ID not found.")
        return

    data = get_maintenance_input(eq)
    eq.update(data)
    flags = get_maintenance_flags(eq)
    maintenance_records.append({"Equipment ID": eq_id, "Availability": data["Availability"], "Flags": flags})
    display_maintenance_result(eq_id, data["Availability"], flags)


def show_maintenance_flags():
    if len(equipment_records) == 0:
        print("No equipment recorded.")
    for eq in equipment_records:
        flags = get_maintenance_flags(eq)
        if len(flags) > 0:
            flag_text = ", ".join(flags)
        else:
            flag_text = "None"
        print(f"Equipment {eq['Equipment ID']} ({eq['Equipment Type']}): "
              f"Availability {eq['Availability']:.2f}% | Flags: {flag_text}")


def maintenance_menu():
    while True:
        choice = get_choice("\nMaintenance Data", ["Update", "Flags", "Back"])
        if choice == "Update":
            update_maintenance()
        elif choice == "Flags":
            show_maintenance_flags()
        else:
            return


# ----------------------------------------------------------------------
# RISK ASSESSMENT
# ----------------------------------------------------------------------
def get_risk_inputs():
    likelihood = get_int("Enter Likelihood (1-5): ", 1, 5)
    consequence = get_int("Enter Consequence (1-5): ", 1, 5)
    return likelihood, consequence


def calculate_risk_score(likelihood, consequence):
    return likelihood * consequence


def classify_risk(risk_score):
    if risk_score >= 1 and risk_score <= 4:
        return "Low"
    elif risk_score >= 5 and risk_score <= 9:
        return "Medium"
    elif risk_score >= 10 and risk_score <= 16:
        return "High"
    else:
        return "Critical"


def store_risk(likelihood, consequence, risk_score, risk_class):
    risk_id = f"RISK-{len(risk_records) + 1:03d}"
    risk_records.append({"Risk ID": risk_id, "Likelihood": likelihood, "Consequence": consequence,
                         "Risk Score": risk_score, "Risk Classification": risk_class})


def display_risk_result(risk_score, risk_class):
    print(f"Risk Score: {risk_score}")
    print(f"Risk Classification: {risk_class}")
    if risk_class == "High" or risk_class == "Critical":
        print("Warning! Notify Safety Officer and Manager.")


def risk_assessment():
    likelihood, consequence = get_risk_inputs()
    risk_score = calculate_risk_score(likelihood, consequence)
    risk_class = classify_risk(risk_score)
    store_risk(likelihood, consequence, risk_score, risk_class)
    display_risk_result(risk_score, risk_class)


# ----------------------------------------------------------------------
# ALERTS
# ----------------------------------------------------------------------
def send_notification(role, alert_type):
    print(f"Notification sent to {role} for alert: {alert_type}")


def display_alert(level, alert_type, source, detail, time_now):
    print("\n" + "=" * 53)
    print("MINING MONITORING ALERT")
    print("=" * 53)
    print(f"[{level}]")
    print(f"[{time_now}] ALERT: {alert_type}")
    print(f"Source ID: {source}")
    if detail != "":
        print(f"Detail: {detail}")
    print("Recommended Action:")
    print("  Inspect and initiate appropriate maintenance/safety procedures.")


def log_alert(alert_type, source, level):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_log.append({"DateTime": time_now, "Alert Type": alert_type, "Source": str(source), "Level": level})
    return time_now


def count_equipment_alert(source):
    for eq in equipment_records:
        if str(eq["Equipment ID"]) == str(source):
            eq["Number of Alerts"] += 1


def raise_alert(alert_type, source, notify_roles, detail, level):
    # The same alert for the same source is only raised once
    key = (alert_type, str(source))
    if key in alert_keys:
        return
    alert_keys.add(key)

    time_now = log_alert(alert_type, source, level)
    count_equipment_alert(source)
    display_alert(level, alert_type, source, detail, time_now)
    for role in notify_roles:
        send_notification(role, alert_type)
    print("=" * 53)


def check_equipment_alerts():
    for eq in equipment_records:
        eid = eq["Equipment ID"]
        if temp_status(eq["Temperature"]) == "CRITICAL":
            raise_alert("Critical Equipment Temperature", eid, ["Maintenance Engineer", "Manager"],
                        f"Temperature {eq['Temperature']} C above critical threshold", "CRITICAL")
        if vib_status(eq["Vibration"]) == "CRITICAL":
            raise_alert("Critical Equipment Vibration", eid, ["Maintenance Engineer", "Manager"],
                        f"Vibration {eq['Vibration']} mm/s above critical threshold", "CRITICAL")

        flags = get_maintenance_flags(eq)
        if "Excessive Downtime" in flags:
            raise_alert("Excessive Downtime", eid, ["Maintenance Engineer", "Manager"],
                        f"Downtime {eq['Downtime']} h", "WARNING")
        if "Overdue" in flags:
            raise_alert("Overdue Maintenance", eid, ["Maintenance Engineer", "Manager"],
                        f"Scheduled {eq['Scheduled Maintenance Date']}", "WARNING")


def check_worker_alerts():
    for w in workers:
        wid = w["Worker ID"]
        if w["PPE Compliance"] == "No":
            raise_alert("PPE Non-Compliance", wid, ["Safety Officer"], "", "WARNING")
        if w["Fatigue Level"] == "High":
            raise_alert("High Fatigue Level", wid, ["Safety Officer"], "", "WARNING")
        if w["Safety Observations"] == "Yes":
            raise_alert("Unsafe Safety Observation", wid, ["Safety Officer", "Manager"], "", "WARNING")


def check_incident_alerts():
    for inc in incidents:
        if inc["Severity"] == "Critical":
            raise_alert("Critical Incident Severity", f"INC-{inc['Incident ID']}",
                        ["Safety Officer", "Manager"], "", "CRITICAL")


def check_risk_alerts():
    for r in risk_records:
        if r["Risk Classification"] == "High" or r["Risk Classification"] == "Critical":
            raise_alert(f"High Risk Classification: {r['Risk Classification']}", r["Risk ID"],
                        ["Safety Officer", "Manager"], "", "CRITICAL")


def check_conditions():
    check_equipment_alerts()
    check_worker_alerts()
    check_incident_alerts()
    check_risk_alerts()


def view_alert_log():
    print("\nALERT LOG")
    if len(alert_log) == 0:
        print("No alerts recorded.")
    for a in alert_log:
        print(f"{a['DateTime']} | {a['Level']:<8} | {a['Source']:<9} | {a['Alert Type']}")


def monitor_alerts(cycles):
    # Optional: checks the conditions a number of times, 2 seconds apart
    # (not linked to the menu, call monitor_alerts(3) to use it)
    for i in range(cycles):
        check_conditions()
        time.sleep(2)
    view_alert_log()


# ----------------------------------------------------------------------
# DASHBOARD AND REPORTS
# ----------------------------------------------------------------------
def calculate_ppe_compliance():
    if len(workers) == 0:
        return 0
    compliant = 0
    for w in workers:
        if w["PPE Compliance"] == "Yes":
            compliant += 1
    return round(compliant / len(workers) * 100, 1)


def calculate_average_availability():
    if len(equipment_records) == 0:
        return 0
    total = 0
    for e in equipment_records:
        total += e["Availability"]
    return round(total / len(equipment_records), 1)


def count_under_maintenance():
    count = 0
    for e in equipment_records:
        if e["Maintenance Status"] == "In Progress":
            count += 1
    return count


def count_critical_alerts():
    count = 0
    for a in alert_log:
        if a["Level"] == "CRITICAL":
            count += 1
    return count


def count_high_risk_workers():
    count = 0
    for w in workers:
        if w["Risk Level"] == "High":
            count += 1
    return count


def count_near_misses():
    total = 0
    for w in workers:
        total += w["Near Misses"]
    return total


def dashboard():
    n_eq = len(equipment_records)
    under = count_under_maintenance()
    print("\n" + "=" * 50)
    print(" MINING MONITORING DASHBOARD")
    print("=" * 50)
    print(f" Total workers ............... {len(workers)}")
    print(f" PPE compliance .............. {calculate_ppe_compliance()}%")
    print(f" High-risk workers ........... {count_high_risk_workers()}")
    print(f" Near misses ................. {count_near_misses()}")
    print(f" Total safety incidents ...... {len(incidents)}")
    print(f" Total equipment ............. {n_eq}")
    print(f" Equipment available ......... {n_eq - under}")
    print(f" Equipment under maintenance . {under}")
    print(f" Avg equipment availability .. {calculate_average_availability()}%")
    print(f" Total alerts ................ {len(alert_log)}")
    print(f" Critical alerts ............. {count_critical_alerts()}")
    print("=" * 50)


def generate_report():
    dashboard()
    view_alert_log()
    print("\nEquipment needing maintenance attention:")
    found = False
    for eq in equipment_records:
        flags = get_maintenance_flags(eq)
        if len(flags) > 0:
            found = True
            print(f"- Equipment {eq['Equipment ID']}: {', '.join(flags)}")
    if not found:
        print("- None")


def manage_users():
    print("\nUser roles and permissions:")
    for p in positions:
        print(f"\n{p}:")
        for f in permissions[p]:
            print("  -", f)


# ----------------------------------------------------------------------
# MAIN MENU
# ----------------------------------------------------------------------
def display_main_menu(pos):
    print(f"\nMAIN MENU ({pos})")
    for f in get_permissions(pos):
        print("-", f)
    print("- View Alert Log")
    print("- Log out")


def call_function(name):
    if name == "View Dashboard":
        dashboard()
    elif name == "Worker Safety Data":
        worker_menu()
    elif name == "Safety Incidents":
        incident_menu()
    elif name == "Equipment Data":
        equipment_menu()
    elif name == "Maintenance Data":
        maintenance_menu()
    elif name == "Risk Assessment":
        risk_assessment()
    elif name == "Generate Reports":
        generate_report()
    elif name == "Manage Users":
        manage_users()


def run_function(choice, pos):
    match = ""
    for f in functions:
        if f.lower() == choice:
            match = f

    if match == "":
        print("Invalid option.")
    elif match not in get_permissions(pos):
        print("Access Denied: you do not have permission for this function.")
    else:
        call_function(match)


def session(pos):
    while True:
        check_conditions()
        display_main_menu(pos)
        choice = input("Choose a function: ").strip().lower()
        if choice == "log out":
            return
        elif choice == "view alert log":
            view_alert_log()
        else:
            run_function(choice, pos)


def main():
    while True:
        pos = login()
        if pos is None:
            print("Goodbye.")
            return
        session(pos)


# ----------------------------------------------------------------------
# MAIN CODE (functions are defined first, then the program starts)
# ----------------------------------------------------------------------
main()
