# Restaurant Menu Ordering System

A Mini Project Report  
Submitted for  
**19EC552 - Microprocessors Laboratory**

By  
G.J.Jeyanthan (Roll No.22BEC170)  
R.S.Selvaraj (Roll No.22BEC181)  
III Year B.E ECE C (V Semester)

Department of Electronics and Communication Engineering  
Academic Year 2024 - 2025

Mepco Schlenk Engineering College  
(An Autonomous Institution Affiliated to Anna University, Chennai)  
Mepco Engineering College (PO), Sivakasi – 626 005  
Virudhunagar (District), Tamil Nadu

---

## Table of Contents

1. [Abstract](#abstract)  
2. [Components](#components)  
3. [Circuit Diagram](#circuit-diagram)  
4. [Transmitter Side Code](#transmitter-side-code)  
5. [Receiver Side Description & Code](#receiver-side-description--code)  
6. [Future Scope](#future-scope)  
7. [Conclusion](#conclusion)  
8. [Menu Card](#menu-card)  

---

## Abstract

The Smart Restaurant Menu Ordering System leverages Arduino technology, an LCD display, a keypad, and Zigbee communication to create an efficient and user-friendly dining experience. Customers interact with a digital menu directly from their tables, facilitating easy selection and ordering of food items. The Arduino microcontroller serves as the central processing unit, managing inputs from the keypad and displaying menu options on the LCD screen.

Using Zigbee, a low-power wireless communication protocol, the system enables seamless data transmission between the customer interface and the restaurant's order management system. This ensures real-time order processing, reducing wait times and enhancing service efficiency. The keypad allows intuitive navigation, item selection, and order submission.

This system not only improves customer satisfaction but also optimizes restaurant operations by streamlining order management and reducing errors, presenting a comprehensive solution for modern dining establishments.

---

## Components

- **Arduino Microcontroller:** Core control unit, processes user inputs, manages hardware, and communicates with Zigbee.
- **LCD Display (20x4):** User interface for displaying menu options, order status, and messages.
- **Keypad (3x4):** Allows users to select items, enter quantities, and place orders.
- **Zigbee Module (XBee):** Facilitates low-power wireless communication between customer interface and central restaurant system.
- **UART:** Serial communication protocol for Arduino and Zigbee.

---

## Circuit Diagram

- **Transmitter Side:**  
  - Arduino reads input from the keypad, displays information on the LCD, and transmits order data via Zigbee.
  - Uses UART for serial communication between Arduino and Zigbee.

- **Receiver Side:**  
  - Receives order data through Zigbee, processes and manages orders, and integrates with a billing and notification system.

---

## Transmitter Side Code

The transmitter (customer table device) uses Arduino code to:
- Display menu and prompts on LCD.
- Accept user input for item code and quantity via keypad.
- Validate and process orders.
- Send orders wirelessly to the receiver using Zigbee.

> See arduino code for complete code.

---

## Receiver Side Description & Code

The receiver (restaurant staff system) is a web application that:
- Connects to the COM port to receive data from the transmitter.
- Processes incoming orders, validates, and stores them.
- Integrates a menu for item lookup and bill calculation.
- Provides a user interface for order notifications, bill generation, and quantity updates.
- Supports bill printing.

### Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Communication:** Web Serial API (for COM port connection)

#### Main Files

- `index.html` — Web interface for staff
- `styles.css` — Styling for the application
- `script.js` — Logic for COM port connection, order processing, and UI interactions

---

## Future Scope

- **Mobile Application Development:** Customer apps for ordering and account management.
- **Real-Time Order Tracking:** Customers can track their orders live.
- **Online Payment Integration:** Seamless and secure payment options.
- **Dynamic Menu Management:** Admin interface for live menu and price updates.
- **Loyalty Rewards Program:** Points or discounts for frequent customers.
- **Data Analytics & Reporting:** Insights into sales, preferences, and inventory.
- **IoT/Smart Kitchen Integration:** Automated order processing with smart kitchen devices.

---

## Conclusion

The Smart Restaurant Menu Ordering System significantly enhances the dining experience by streamlining the ordering process, reducing errors, and expediting service. This allows restaurant staff to focus on exceptional customer service and provides valuable analytics for management. Its scalable design allows for future enhancements such as online payments and mobile apps.

---

## Menu Card

| Code | Item Name                 | Price (₹) |
|------|---------------------------|:---------:|
| 00   | Idli                      |    10     |
| 01   | Dosa                      |    25     |
| 02   | Sambar Rice               |    50     |
| 03   | Vegetable Biryani         |    80     |
| 04   | Pongal                    |    40     |
| 05   | Vada                      |    12     |
| 06   | Chettinad Chicken Curry   |   150     |
| 07   | Fish Curry                |   180     |
| 08   | Mutton Biryani            |   220     |
| 09   | Parotta                   |    15     |

---

## Authors

- G.J.Jeyanthan (22BEC170)
- R.S.Selvaraj (22BEC181)

---

## License

This project is for academic demonstration purposes.
