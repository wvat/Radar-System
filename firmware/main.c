//Fred Vatnsdal
//FMCW Radar 

#include <avr/io.h>
#include <stdio.h>

#define N_SAMPLES 128		//number of samples per frame
#define PREAM 0xAA		
#define START 0x53		//start flag
#define END 0x45		//end flag

void init_adc();
void init_usart();
void sample_signal(uint8_t[]);
int start_conversion(char);
void usart_transmit(int);
uint8_t transmit_data(uint8_t[],int);

int main(void){
	init_adc();
	init_usart();
	uint8_t checksum;
	uint8_t samples[N_SAMPLES];
	
	while(1){
		sample_signal(samples);				//Acquire samples
		usart_transmit(PREAM);				//Send two preamble bytes
		usart_transmit(PREAM);
		usart_transmit(START);				//Send start flag
		checksum = transmit_data(samples, N_SAMPLES);	//Send samples
		usart_transmit(checksum);
		usart_transmit(END);				//Send end flag			
	}
}

void init_adc(){
	ADMUX = (1<<REFS0);
	ADCSRA = (1<<ADEN)|(1<<ADPS2)|(1<<ADPS1); //ADPS2,ADPS1,ADPS0 (currently /128)
	return;
}

void init_usart(){
	UBRRH = 0;
	UBRRL = 0x33;
	UCSRB = (1<<RXEN)|(1<<TXEN); //enable TX and RX.
	//Synch, 8 bits, even parity, 2 stop bits.
	UCSRC = (1<<URSEL)|(1<<USBS)|(1<<UPM1)|(1<<UCSZ1)|(1<<UCSZ0); 
	return;
}

void sample_signal(uint8_t samples[]){
	int i;
	int sample;
	for(i = 0; i < N_SAMPLES; i++){
		sample = start_conversion(0);		//ADC 0
		sample = sample >> 2;
		samples[i] = sample;			//Store samples
	}
	return;
}

int start_conversion(char channel){
	channel = channel & 0x07;			//Select channel (0-7)
	ADMUX = ADMUX | channel;			//""
	ADCSRA |= (1<<ADSC);				//Start conversion
	while(ADCSRA & (1<<ADSC));			//Wait until conversion complete
	return(ADC);					//Return the ADC reading (10 bit)
}

void usart_transmit(int data){	
	while(!(UCSRA & (1<<UDRE)));			//Wait until UDRE is set
	UDR = data;					//Transmit
}

uint8_t transmit_data(uint8_t samples[], int numSam){
	int i;		
	uint8_t checksum = 0;				//Iterator
	for(i = 0; i < numSam; i++){
		checksum += samples[i];
		while(!(UCSRA & (1<<UDRE)));		//Wait until UDRE is set
		UDR = samples[i];			//Transmit
	}
	return checksum;
}
