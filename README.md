# Track Stars 🏃‍♂️💨🚇
**Winner: General Track 1st Place @ MIT Blueprint 2026**

![Banner](https://plume.hackmit.org/api/v3/projects/pr-NuMlydzUH3O6ZCO/image?t=1773272315105)

## 💡 Inspiration
Ever been running late to class because the Red Line to Kendall is just too slow? We know you've thought to yourself, *"I could literally walk faster than this train."* Boston commuters joke constantly about racing and beating the T. So, we turned that frustration into a challenge: **what if your steps actually competed against MBTA line speeds in real time?** Instead of just complaining about delays, we built a way to outrun them.

---

## 🚀 What it Does
**Track Stars** is an interactive hardware-software system that allows you to race against real-time MBTA trains. 

We built a wearable ankle device equipped with an ultrasonic sensor that tracks your step count and calculates your running speed. This data is streamed live via MQTT to a Flask backend, which simultaneously pulls live speed data for active trains on the Red, Green, and Orange lines using the MBTA API. A sleek web UI then compares your physical speed against the trains, letting you know if you're actually faster than the T!

---

## 🛠️ How We Built It

### Hardware
* **Microcontroller:** Arduino UNO R4 WiFi powered by a portable power bank.
* **Sensors & IO:** Ultrasonic sensor (for stride detection), a calibration button, and 3 LED indicators (Green, Yellow, Red) to show speed tiers.
* **Mounting:** Classic hackathon engineering—duct-taped securely to the user's ankle! :)
* **Logic:** The Arduino measures the distance to the ground. When the foot comes down (distance falls within a set deadband), it counts a step. By measuring the time between steps, we calculate step cadence and multiply it by an average stride length to get the real-time running speed in meters per second (m/s).

### Backend & Server
* **Server:** Python with Flask.
* **Communication:** Hardware and server communicate over MQTT (via `test.mosquitto.org`). 
* **Real-Time Data:** The backend utilizes Server-Sent Events (SSE) to push live speed updates to the frontend without requiring constant page reloads.
* **MBTA Integration:** We query the official `api-v3.mbta.com` to calculate the current speed of trains between specific segment stops (e.g., Park St → Downtown Crossing). By comparing the departure and arrival times of the exact same train ID, we calculate the train's actual transit speed in m/s and km/h.

### Frontend
* **Stack:** HTML, CSS, JavaScript.
* **UI:** A beautiful, responsive web interface that displays the user's live speed alongside the real-time speeds of the Green, Red, and Orange lines.

---

## ⚠️ Challenges We Ran Into
We initially planned to use an accelerometer to detect footsteps, but we had to adapt to the hardware the Blueprint team stocked. We rathed pivoted to using a downward-facing **ultrasonic sensor** to measure distance to the ground and detect when a foot was planted. Additionally, our initial battery packs failed, so we quickly re-engineered the board to run off a standard USB power bank. 

---

## 🏆 Accomplishments We're Proud Of
* **Resourcefulness:** Successfully calculating speed and stride using an ultrasonic sensor when an accelerometer wasn't available.
* **Full-Stack IoT:** Seamlessly integrating an edge hardware device with a cloud MQTT broker, a Python backend, and a web frontend.
* **Live Open Data:** Successfully navigating and implementing the MBTA API to calculate real-world transit speeds dynamically. 

---

## 🔮 What's Next
* **Multiplayer Mode:** Add multiple hardware nodes so friends can race each other *and* the train simultaneously.
* **Sensor Fusion:** Integrate secondary sensors (like an actual IMU/accelerometer) to improve the accuracy of the stride and speed calculations.
* **Extended Hardware Controls:** Add more buttons to the ankle module to manually trigger race starts, stopwatches, or lap times.

---

## 👥 The Team
* **Max Kendall:** Wired the ankle device, set up MQTT, and linked the hardware with the backend server and UI.
* **Dinesh Babu:** Built the API integration and backend logic to fetch and parse real-time MBTA train data for the Red, Green, and Orange lines. Provided the main inspiration/idea for the project.
* **Ben Vaccaro:** Handled hardware design, core embedded functionality, and front-end design/implementation.
* **Abner Machuca Diaz:** Led the UI design, front-end development, and was a true runner who validated the project.

---
*Created with ❤️ in Cambridge, MA for MIT Blueprint 2026.*
