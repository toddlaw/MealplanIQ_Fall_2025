import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ShoppingList } from './shopping-list-landing-page.interface';

@Component({
  selector: 'app-shopping-list-landing-page',
  templateUrl: './shopping-list-landing-page.component.html',
  styleUrls: ['./shopping-list-landing-page.component.css'],
})
export class ShoppingListLandingPageComponent implements OnInit {
  data: { shoppingListData: ShoppingList[]; minDate: string; maxDate: string } =
    {
      shoppingListData: [],
      minDate: '',
      maxDate: '',
    };

  constructor(@Inject(MAT_DIALOG_DATA) private dialogData: any) {
    this.data = dialogData;
  }

  ngOnInit(): void {
    console.log(
      'The number of items in shopping list: ',
      this.data.shoppingListData.length
    );
  }
}
