import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ShoppingList } from './shopping-list.interface';

@Component({
  selector: 'app-shopping-list',
  templateUrl: './shopping-list.component.html',
})
export class ShoppingListComponent implements OnInit {
  data: ShoppingList[] = []; // Initialize the "data" property with an empty object
  constructor(@Inject(MAT_DIALOG_DATA) private dialogData: any) {}

  ngOnInit(): void {
    this.data = this.dialogData; // Assign the received data to the local variable
    console.log('Received data:', this.data);
  }
}
