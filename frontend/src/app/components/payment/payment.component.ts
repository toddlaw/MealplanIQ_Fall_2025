import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';

declare var Stripe: any; // Declare Stripe to avoid TypeScript errors

@Component({
  selector: 'app-payment',
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.css']
})
export class PaymentComponent implements OnInit, OnDestroy {
  stripe: any;
card: any;
cardHandler = this.onChange.bind(this);

@ViewChild('cardElement', {static: true}) cardElement!: ElementRef; // Add '!' non-null assertion operator

constructor(private http: HttpClient) {}

ngOnInit() {
    this.stripe = Stripe('your_public_stripe_key'); // Use your Stripe public key
    const elements = this.stripe.elements();
    this.card = elements.create('card');
    this.card.mount(this.cardElement.nativeElement);
    this.card.addEventListener('change', this.cardHandler);
}

  ngOnDestroy() {
    this.card.removeEventListener('change', this.cardHandler);
    this.card.destroy();
  }

onChange({ error }: { error: any }) {
    const displayError = document.getElementById('card-errors');
    if (displayError) {
        if (error) {
            displayError.textContent = error.message;
        } else {
            displayError.textContent = '';
        }
    }
}

submitPayment() {
    const extraDetails = {
        name: 'Optional Name', // You can add additional card information here
    };
    this.stripe.createToken(this.card, extraDetails).then((result: any) => { // Explicitly type 'result' as 'any'
        if (result.error) {
            // Inform the customer that there was an error.
            var errorElement = document.getElementById('card-errors');
            if (errorElement) {
                errorElement.textContent = result.error.message;
            }
        } else {
            // Send the token to your server.
            this.sendTokenToServer(result.token);
        }
    });
}

sendTokenToServer(token: any) {
    this.http.post('http://127.0.0.1:5000/create-charge', {
        token: token.id,
        amount: 2000 // $20, for example
    }).subscribe(
        data => console.log('Success:', data),
        error => console.error('Error:', error)
    );
}
}