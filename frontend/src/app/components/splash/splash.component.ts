import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ShoppingList } from './../dialogues/shopping-list/shopping-list.interface'; // Import the interface if needed
import { ShoppingListComponent } from './../dialogues/shopping-list/shopping-list.component'; // Import the component if needed
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-splash',
  templateUrl: './splash.component.html',
  styleUrls: ['./splash.component.css'],
})
export class SplashComponent {
  shoppingListData: ShoppingList[] = [
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

  constructor(public dialog: MatDialog) {}

  openShoppingListDialog(): void {
    console.log(this.shoppingListData);
    const dialogRef = this.dialog.open(ShoppingListComponent, {
      width: '500px', // Set the width of the dialog
      data: this.shoppingListData, // Pass your shopping list data to the dialog
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log('The dialog was closed');
    });
  }
}
