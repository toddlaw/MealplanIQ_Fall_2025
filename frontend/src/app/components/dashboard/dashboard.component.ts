import { Component, OnInit } from '@angular/core';
import { UsersService } from 'src/app/services/users.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})

export class DashboardComponent implements OnInit {
  user: any;

  Profile_info = [
    {'name': 'First Name', 'placeholder': 'Enter your first name', 'type': 'firstName', 'error': ''},
    {'name': 'Last Name', 'placeholder': 'Enter your last name', 'type': 'lastName', 'error': ''},
    {'name': 'Email', 'placeholder': 'Enter your email', 'type': 'email', 'error': ''},
    {'name': 'Phone', 'placeholder': 'Enter your phone', 'type': 'phone', 'error': ''},
    {'name': 'Address', 'placeholder': 'Enter your address', 'type': 'address', 'error': ''},
    {'name': 'Age', 'placeholder': 'Enter your age', 'type': 'age', 'error': ''},
    {'name': 'Height', 'placeholder': 'Enter your height', 'type': 'height', 'error': ''},
    {'name': 'Weight', 'placeholder': 'Enter your weight', 'type': 'weight', 'error': ''},
  ]

  constructor() { }

  

  ngOnInit(): void {
  }

}
