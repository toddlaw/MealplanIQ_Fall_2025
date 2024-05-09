import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

declare var Stripe: any;
// var stripe = Stripe()

@Component({
  selector: 'app-payment',
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.css'],
})
export class PaymentComponent implements OnInit {
  stripe: any; // Stripe instance
  card: any; // Card instance
  email: string = '';
  plan_type: string = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.stripe = Stripe(environment.STRIPE_PUBLIC_KEY);
    let elements = this.stripe.elements();
    this.card = elements.create('card');
    this.card.mount('#card-element'); // Mount the card element to a div with id 'card-element'
  }

  handleForm(e: any) {
    e.preventDefault();
    this.stripe.createToken(this.card).then((result: any) => {
      if (result.error) {
        console.log('Stripe error: ', result.error);
      } else {
        // Send the token to server
        this.http
          .post('http://localhost:5000/create-subscription', {
            token: result.token.id,
            email: this.email,
            plan_type: this.plan_type,
          })
          .subscribe((data) => {
            console.log('Payment succeeded: ', data);
          });
      }
    });
  }
}
