// Define the Menu
const menu = [
    { code: 0, name: 'Idli', price: 10},
    { code: 1, name: 'Dosa', price: 25 },
    { code: 2, name: 'Sambar Rice', price: 50 },
    { code: 3, name: 'Vegetable Biryani', price: 80 },
    { code: 4, name: 'Pongal', price: 40 },
    { code: 5, name: 'Vada', price: 12 },
    { code: 6, name: 'Chettinad Chicken Curry', price: 150 },
    { code: 7, name: 'Fish Curry', price: 180 },
    { code: 8, name: 'Mutton Briyani', price: 220 },
    { code: 9, name: 'Parotta', price: 15 }
];


let port = null;
let orders = []; // To store received orders
let orderCounter = 1; // Counter to keep track of order numbers
let receivedData = '';  // Buffer to store incoming data

// Connect to the COM port
async function connectCOMPort() {
    try {
        if (!port) {
            port = await navigator.serial.requestPort();
            await port.open({ baudRate: 9600 });
            document.getElementById('comStatus').textContent = "Connected to COM port!";
            listenForData(); // Start listening for incoming data
        }
    } catch (err) {
        document.getElementById('comStatus').textContent = "Failed to connect: " + err;
    }
}

// Listen for incoming data from the COM port
async function listenForData() {
    const reader = port.readable.getReader();
    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) {
                console.log("Stream closed");
                break;
            }
            if (value) {
                receivedData += new TextDecoder().decode(value);
                console.log("Received raw data:", receivedData); // Log received raw data for debugging

                // Process the incoming data when 'end of order' is detected
                if (receivedData.includes('End of Order')) {
                    processOrderData(receivedData);
                    receivedData = ''; // Clear buffer after processing
                }
            }
        }
    } catch (err) {
        console.error('Error reading data:', err);
    } finally {
        reader.releaseLock();
    }
}

// Process the received order data
function processOrderData(data) {
    const cleanedData = data.split('\n').map(line => line.trim()).filter(line => line !== ''); // Split data by lines and trim
    const items = cleanedData.slice(0, -1);  // Remove 'End of Order' line

    console.log("Parsed items from received data:", items); // Log parsed items for debugging

    // Check if the received data has valid pairs of item code and quantity
    if (items.length % 2 === 0) {
        let orderItems = [];
        for (let i = 0; i < items.length; i += 2) {
            const code = parseInt(items[i]);
            const quantity = parseInt(items[i + 1]);
            const menuItem = menu.find(item => item.code === code);
            if (menuItem) {
                orderItems.push({
                    code,
                    name: menuItem.name,
                    quantity,
                    price: menuItem.price,
                    total: menuItem.price * quantity
                });
            }
        }

        // Add the processed order to the orders array
        orders.push({
            orderNumber: orderCounter++,
            items: orderItems
        });

        displayOrderSummary(); // Update the order notification
    } else {
        document.getElementById('comStatus').textContent = "Error: Invalid order data received.";
    }
}

// Display order summary in the notification
function displayOrderSummary() {
    const notification = document.getElementById('notification');
    notification.innerHTML = '';

    // Display each order in the notification
    orders.forEach(order => {
        const orderElement = document.createElement('div');
        orderElement.textContent = `Order ${order.orderNumber}`;
        orderElement.onclick = () => displayBill(order);
        notification.appendChild(orderElement);
    });
}

// Display the bill for an order
function displayBill(order) {
    const billBody = document.getElementById('billBody');
    billBody.innerHTML = ''; // Clear previous bill
    let grandTotal = 0;

    // Create rows for each item in the order
    order.items.forEach((item, index) => {
        const row = document.createElement('tr');
        const total = item.quantity * item.price;
        grandTotal += total;

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.code}</td>
            <td>${item.name}</td>
            <td contenteditable="true" oninput="updateTotal(this, ${item.price})">${item.quantity}</td>
            <td>${item.price}</td>
            <td>${total}</td>
        `;
        billBody.appendChild(row);
    });

    // Display grand total
    const totalRow = document.createElement('tr');
    totalRow.innerHTML = `<td colspan="5">Overall Total:</td><td>${grandTotal}</td>`;
    billBody.appendChild(totalRow);

    document.getElementById('billContainer').style.display = 'block'; // Show the bill container
    showSection('processBill'); // Switch to the bill section
}

// Update the total amount when quantity is edited
function updateTotal(cell, price) {
    const quantity = parseInt(cell.textContent);
    const totalCell = cell.parentElement.cells[5];
    totalCell.textContent = quantity * price;

    // Update overall total
    const billBody = document.getElementById('billBody');
    let grandTotal = 0;
    for (let i = 0; i < billBody.rows.length - 1; i++) {
        grandTotal += parseInt(billBody.rows[i].cells[5].textContent);
    }
    billBody.rows[billBody.rows.length - 1].cells[1].textContent = grandTotal; // Update overall total
}

// Send order data to the COM port
// Send updated quantity for a specific item code
function sendOrder() {
    const itemCode = document.getElementById('item-code').value;
    const quantity = document.getElementById('quantity').value;
    quantity = quantity < 10 ? `0${quantity}` : quantity;
    const data = `${itemCode}${quantity}`; // Ensure correct format

    if (port) {
        const writer = port.writable.getWriter();
        const encoded = new TextEncoder().encode(data); // Send data as new line separated
        writer.write(encoded);
        writer.releaseLock();
        document.getElementById('status').textContent = "Order sent successfully!";
    } else {
        document.getElementById('status').textContent = "COM port not connected.";
    }
}




// Switch between sections
function showSection(section) {
    document.querySelector('.update-quantity').style.display = section === 'updateQuantity' ? 'block' : 'none';
    document.getElementById('billContainer').style.display = section === 'processBill' ? 'block' : 'none';
}

// Hide all sections except main
function showMain() {
    document.querySelector('.update-quantity').style.display = 'none';
    document.getElementById('billContainer').style.display = 'none';
}

// Print the bill
function printBill() {
    window.print();
}
