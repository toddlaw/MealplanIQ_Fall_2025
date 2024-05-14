import { Component, OnInit } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { ShoppingList } from './../dialogues/shopping-list/shopping-list.interface'; // Import the interface if needed
import { ShoppingListComponent } from './../dialogues/shopping-list/shopping-list.component'; // Import the component if needed
import { Overlay } from '@angular/cdk/overlay';
import { NoopScrollStrategy } from '@angular/cdk/overlay';

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
}
