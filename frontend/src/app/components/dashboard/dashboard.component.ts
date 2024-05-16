import { Component, OnInit } from '@angular/core';
import { UsersService } from 'src/app/services/users.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  user: any;

  dashboard_buttons = [
    { name: 'Profile', link: '/profile' },
    { name: 'Shopping List', link: '/shoppingList' },
    { name: 'Nutrition Report', link: '/report' },
    { name: 'Manage Subscription', link: '/subscription' },
  ];

  constructor() { }

  ngOnInit(): void {
  }

}
