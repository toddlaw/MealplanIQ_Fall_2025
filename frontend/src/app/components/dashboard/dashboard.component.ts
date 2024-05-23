import { Component, OnInit } from '@angular/core';
import { UsersService } from 'src/app/services/users.service';
import { ShoppingList } from '../dialogues/shopping-list/shopping-list.interface';
import { ShoppingListComponent } from './../dialogues/shopping-list/shopping-list.component'; 
import { Overlay } from '@angular/cdk/overlay';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { GeneratePopUpComponent } from '../dialogues/generate-pop-up/generate-pop-up.component';

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

  shoppingListData: ShoppingList[] = [
    {
      date: '2024-05-11',
      'shopping-list': [
        { name: 'Chicken', quantity: '400g' },
        { name: 'Lemon', quantity: '2' },
        { name: 'Herbs', quantity: '2' },
      ],
    },
    {
      date: '2024-05-11',
      'shopping-list': [
        { name: 'Chicken', quantity: '400g' },
        { name: 'Lemon', quantity: '2' },
        { name: 'Herbs', quantity: '2' },
      ],
    },
    {
      date: '2024-05-11',
      'shopping-list': [
        { name: 'Chicken', quantity: '400g' },
        { name: 'Lemon', quantity: '2' },
        { name: 'Herbs', quantity: '2' },
      ],
    },
    {
      date: '2024-05-11',
      'shopping-list': [
        { name: 'Chicken', quantity: '400g' },
        { name: 'Lemon', quantity: '2' },
        { name: 'Herbs', quantity: '2' },
      ],
    },
    // Add more shopping list data items as needed
  ];

  constructor(public dialog: MatDialog, private overlay: Overlay) {}
  ngOnInit(): void {
    // throw new Error('Method not implemented.');
  }

  openShoppingListDialog(): void {
    console.log(this.shoppingListData);
    const dialogConfig = new MatDialogConfig();
    dialogConfig.width = '500px'; // Set the width of the dialog
    dialogConfig.data = this.shoppingListData; // Pass your shopping list data to the dialog
    dialogConfig.autoFocus = false; // Disable auto-focus
    const dialogRef = this.dialog.open(ShoppingListComponent, dialogConfig);

    dialogRef.afterOpened().subscribe(() => {
      const dialogContent = document.querySelector('.popup-max-height');
      console.log(dialogContent);
      if (dialogContent) {
        dialogContent.scrollTop = 0;
      }
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log('The dialog was closed');
    });
  }

  manageSubscription() {
    const subscription_type_id = localStorage.getItem('subscription_type_id');
    if (subscription_type_id === '1' || subscription_type_id === '2') {
      const email = localStorage.getItem('email');
      const url = 'https://billing.stripe.com/p/login/test_bIY4h4eET9xWbZe9AA?prefilled_email=' + email;
      window.location.href = url;
    } else if (subscription_type_id === '3') {
      this.openDialog(
        "You're currently not subscribed.",
        "<div class='text-center'>Interested in For-pay feature?<br>Click <strong>'Subscribe'</strong> to get started.</div>",
        '/payment',
        'Subscribe'
      );
    }
  }

  openDialog(title: string, message: string, redirectUrl: string, confirmLabel: string) {
    const dialogRef = this.dialog.open(GeneratePopUpComponent, {
      width: '500px',
      data: { title, message, confirmLabel },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        window.location.href = redirectUrl;
      }
    });
  }
}
