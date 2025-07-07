     // include the library code:
#include <LiquidCrystal.h>
#include <Keypad.h>
#include <Arduino.h>

// Initialize the LiquidCrystal library with the pins connected to the LCD
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Keypad setup
const byte ROWS = 4; // Four rows
const byte COLS = 3; // Three columns
char keys[ROWS][COLS] = {
  {'1', '2', '3'},
  {'4', '5', '6'},
  {'7', '8', '9'},
  {'*', '0', '#'}
};
byte rowPins[ROWS] = {9,8,7,6}; // Connect to the row pinouts of the keypad
byte colPins[COLS] = {A2,A1,A0};  // Connect to the column pinouts of the keypad
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
unsigned int quant[10] = {10, 16, 10, 10, 10, 10, 10, 10, 10, 10};
void setup() {
  Serial.begin(9600);
  unsigned char temp_str[2]; 
char ab=0;
char item_code[2];
    char flag =0;
  	unsigned char quantity[3];   // To store quantity (up to 2 digits)
    unsigned char idx = 0;
    unsigned int order[20];
    unsigned char idx1 = 0;
    unsigned char idx2 = 0;   
    char ba=0;
    char key;
  menu1:
  lcd.begin(20, 4);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome to the");
  lcd.setCursor(0, 1);
  lcd.print("Hotel");
  lcd.setCursor(0, 2);
  lcd.print("Press * to");
  lcd.setCursor(0, 3);
  lcd.print("Continue");
  idx2=0;
lq1:		if(Serial.available() > 0)
		{
      uart_receive();
		goto menu1;
		}
lq2: while(keypad.getKey()!='*')
		{
			if (Serial.available() > 0)
				goto lq1;
			goto lq2;
		};

   menu:
		item_code[0]='\0';
	  item_code[1]='\0';
	  temp_str[0]='\0';
	  temp_str[1]='\0';
	  quantity[0]='\0';
	  quantity[1]='\0';
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enter the item");
  lcd.setCursor(0, 1);
  lcd.print("code and press *");
  lcd.setCursor(0, 2);
  lcd.print("to continue");
  idx = 0;
  idx1=0;
  lcd.setCursor(0, 3);
  while(1)
  {
    key=keypad.getKey();
    if(key!='\0'){
    		if(key!='#'&&key!='*'){
            lcd.print(key);
            item_code[idx++]=key;
    }
    else if(key=='*'&&idx==0){
        	  lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("INVALID ITEM");
            lcd.setCursor(0, 1);
            lcd.print("CODE");
            delay(1000);
            goto menu;             	
        		}
      else if(key=='*'&&idx!=0){
			if(item_code[0]=='0'&&idx<3){
				goto l2;
			 }
			else{
			 	   lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("INVALID ITEM");
            lcd.setCursor(0, 1);
            lcd.print("CODE");
            delay(1000);
            goto menu;  
			 }
			 l2:
			         lcd.clear();
			 	         lcd.setCursor(0, 0);
				        lcd.print("Enter quantity");
                lcd.setCursor(0, 2);
                lcd.print("Available: ");
			          ab=0;
			          ab = atoi(item_code);
                sprintf(temp_str, "%d", quant[ab]);
                lcd.print((char*)temp_str);
                lcd.setCursor(0, 3);
                lcd.print("#-place order");
                lcd.setCursor(0, 1);
                idx1 = 0;  // Reset quantity index

                while(1) {
                    key = keypad.getKey();
                    if(key != '\0') {
                        if (key != '*' && key != '#') {
                            lcd.print(key);
                            quantity[idx1++] = key;  // Store the quantity input
                        }
                        else if (key == '#'&& idx1!=0) { 
                            quantity[idx1] = '\0';
													  ba=atoi(quantity);
													  if(ba<=quant[ab]){
														quant[ab]=quant[ab]-ba;
														order[idx2++]=ab;
														order[idx2++]=ba;
														lcd.clear();
			 	                    lcd.setCursor(0, 0);
														lcd.print("Order placed");
														temp_str[0]='\0';
	                          temp_str[1]='\0';
                            order1(order, idx2);
                            delay(1000);
                            goto menu1;  // Return to the menu
                        }
														else{
														lcd.clear();
                             lcd.setCursor(0, 0);
                             lcd.print("Invalid");
														 lcd.setCursor(0, 1);
                             lcd.print("quantity");
															delay(1000);
															quantity[0]='\0';
	                            quantity[1]='\0';
															goto l2;
														}
											}
												else if (key == '*' && idx1!=0){
													  ba=atoi(quantity);
													  if(ba<=quant[ab]&&ba!=0){
														quant[ab]=quant[ab]-ba;
														order[idx2++]=ab;
														order[idx2++]=ba;
														goto menu;
												}
														else{
														lcd.clear();
                             lcd.setCursor(0, 0);
                             lcd.print("Invalid");
															 lcd.setCursor(0, 1);
                             lcd.print("quantity");
															delay(1000);
															quantity[0]='\0';
	                            quantity[1]='\0';
															goto l2;
														}
											}
                        else if ((key == '#' || key == '*') &&idx1==0){
                        	   lcd.clear();
                             lcd.setCursor(0, 0);
                             lcd.print("Quantity not");
                              lcd.setCursor(0, 1);
                             lcd.print("Entered");
                             delay(1000);
                             lcd.clear();
													   goto l2;
						              }
	
					
                    }
                }
            }
} 
  }
}
void order1(unsigned int *a, unsigned int idx2) {
    char temp_str[10];  // Buffer to hold each value as a string
    unsigned int *ptr = a;  // Pointer to iterate through the array

    while (ptr < a + idx2) {
        // Convert and send the item code
        snprintf(temp_str, sizeof(temp_str), "%u", *ptr);  // Convert item code to string
        Serial.println(temp_str);  // Send item code followed by newline

        ptr++;  // Move to the next value (quantity)

        // Convert and send the quantity
        snprintf(temp_str, sizeof(temp_str), "%u", *ptr);  // Convert quantity to string
        Serial.println(temp_str);  // Send quantity followed by newline

        ptr++;  // Move to the next item code
    }

    Serial.println("End of Order");  // Signal end of order
}
void uart_receive() {
    unsigned char received_item = 0;
    unsigned char received_quantity = 0;

    // Wait for the first character (item code, 0-9)
    while (Serial.available() == 0);  // Wait for the item code to be received
    received_item = Serial.read() - '0';  // Convert ASCII to digit (0-9)

    // Wait for the second character (first digit of quantity)
    while (Serial.available() == 0);  // Wait for the first digit of quantity
    received_quantity = (Serial.read() - '0') * 10;  // Multiply by 10 to get tens place

    // Wait for the third character (second digit of quantity)
    while (Serial.available() == 0);  // Wait for the second digit of quantity
    received_quantity += (Serial.read() - '0');  // Add the units place

    // Validate item code and update the quantity safely
    if (received_item < 10 && received_quantity < 100) {  // Ensure item and quantity are valid
        quant[received_item] = quant[received_item]+received_quantity;  // Update the item quantity
        
        lcd.clear();  // Clear the LCD
        lcd.print("Item ");  // Display item label
        lcd.print(received_item);  // Display item code
        lcd.print(" updated."); 
        delay(1000); // Display updated message
        return;
    } else {
        Serial.println("Update failed");
        return;
    }
}
void loop() {
    
}
