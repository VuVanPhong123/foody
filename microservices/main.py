import subprocess
import os
import time

services = [
    ("ingredient_service", 8000),
    ("order_service", 8001),
    ("revenue_service", 8002),
    ("food_service", 8003),       
    ("cart_service", 8004),
    ("orderinfo_service", 8005),
    ("onlineorder_service", 8006),
    ("history_service", 8007),
    ("review_service", 8008),
    ("chat_service", 8009),
    ("auth_service", 8010),
    ("auth_service_cus", 8011),
    ("menu_chat_service", 8012)
]

processes = []

print(" Starting all microservices...\n")

for service_folder, port in services:
    main_file = os.path.join("microservices", service_folder, "main.py")
    if os.path.exists(main_file):
        print(f" Launching {service_folder} (port {port})")
        p = subprocess.Popen(["python", main_file])
        processes.append(p)
        time.sleep(0.5) 
    else:
        print(f" main.py not found in {service_folder}, skipping...")

print("\n All services launched.")
print(" Press Ctrl+C to stop all services.")

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\n Stopping all services...")
    for p in processes:
        p.terminate()
