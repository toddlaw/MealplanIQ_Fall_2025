import { Component, OnInit } from '@angular/core';
import { UsersService } from 'src/app/services/users.service';
import { AuthService } from 'src/app/services/auth.service';
import { ShoppingList } from '../dialogues/shopping-list/shopping-list.interface';
import { ShoppingListComponent } from './../dialogues/shopping-list/shopping-list.component';
import { Overlay } from '@angular/cdk/overlay';
import { Router } from '@angular/router';
import { activityLevels, genders } from '../landing/form-values';
import { HttpClient } from '@angular/common/http';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { GeneratePopUpComponent } from '../dialogues/generate-pop-up/generate-pop-up.component';
import { NutritionChartComponent } from '../dialogues/nutrition-chart/nutrition-chart.component';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  user: any;
  userName: string = '';
  selected_unit: string = '';
  subscriptionType: string = '';
  hasSubscription: boolean = false;

  Profile_info = [
    {
      name: 'Name',
      placeholder: 'Enter your name',
      type: 'user_name',
      error: '',
      value: '',
    },
    {
      name: 'Email',
      placeholder: 'Enter your email',
      type: 'email',
      error: '',
      value: '',
      readonly: true,
    },
    {
      name: 'Age',
      placeholder: 'Enter your age',
      type: 'age',
      error: '',
      value: '',
    },
    {
      name: 'Gender',
      placeholder: 'Select your gender',
      type: 'gender',
      error: '',
      value: '',
      options: genders,
    },
    {
      name: 'Height',
      placeholder: 'Enter your height',
      type: 'height',
      error: '',
      value: '',
    },
    {
      name: 'Weight',
      placeholder: 'Enter your weight',
      type: 'weight',
      error: '',
      value: '',
    },
    {
      name: 'Activity Level',
      placeholder: 'Select your activity level',
      type: 'activity_level',
      error: '',
      value: '',
      options: activityLevels,
    },
  ];

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

  constructor(
    public dialog: MatDialog,
    private overlay: Overlay,
    private router: Router,
    private http: HttpClient,
    private authService: AuthService
  ) {}

  async ngOnInit(): Promise<void> {
    this.showSubscriptionStatus();
    try {
      const data: any = await this.http
        .get(
          'http://127.0.0.1:5000/api/landing/profile/' +
            localStorage.getItem('uid')
        )
        .toPromise();

      console.log(data);
      this.user = data;
      this.prefillProfileInfo(this.user);
      this.userName = this.user.user_name;
      this.selected_unit = this.user.selected_unit;
    } catch (error) {
      console.error(error);
    }
  }

  prefillProfileInfo(data: any) {
    this.Profile_info = this.Profile_info.map((info) => {
      if (data[info.type]) {
        return { ...info, value: data[info.type] };
      }
      return info;
    });
  }

  getSuffix(type: string): string {
    if (type === 'weight') {
      return this.selected_unit === 'imperial' ? 'lbs' : 'kg';
    } else if (type === 'height') {
      return this.selected_unit === 'imperial' ? 'in' : 'cm';
    }
    return '';
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
    const email = localStorage.getItem('email');
    const subscription_type_id = localStorage.getItem('subscription_type_id');
    // 1: monthly, 2: yearly, 3: free-trial for signed up user
    if (subscription_type_id === '1' || subscription_type_id === '2') {
      // for stripe test mode
      const url = 'https://billing.stripe.com/p/login/test_bIY4h4eET9xWbZe9AA?prefilled_email=' + email;

      // for stripe live mode
      // const url = 'https://billing.stripe.com/p/login/bIY7sxbu7c14g7eeUU?prefilled_email=' + email;

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

  openDialog(
    title: string,
    message: string,
    redirectUrl: string,
    confirmLabel: string
  ) {
    const dialogRef = this.dialog.open(GeneratePopUpComponent, {
      width: '500px',
      data: { title, message, confirmLabel },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.router.navigate([redirectUrl]);
      }
    });
  }

  showSubscriptionStatus(): void {
    const subscriptionTypeId = localStorage.getItem('subscription_type_id');
    if (subscriptionTypeId === '1' || subscriptionTypeId === '2') {
      this.subscriptionType = subscriptionTypeId === '1' ? 'monthly' : 'yearly';
      this.hasSubscription = true;
    } else if (subscriptionTypeId === '3') {
      this.hasSubscription = false;
    }
  }

  logout() {
    this.authService.logout().subscribe(() => {
      localStorage.removeItem('email');
      localStorage.removeItem('uid');
      this.router.navigate(['/']);
    });
  }

  openNutrition() {
    console.log(this.shoppingListData);
    const dialogConfig = new MatDialogConfig();
    dialogConfig.width = '500px'; // Set the width of the dialog
    dialogConfig.data = this.shoppingListData; // Pass your shopping list data to the dialog --change with nutition chart
    dialogConfig.autoFocus = false; // Disable auto-focus
    const dialogRef = this.dialog.open(NutritionChartComponent, dialogConfig);

    dialogRef.afterOpened().subscribe(() => {
      const dialogContent = document.querySelector('.popup-max-height');
      if (dialogContent) {
        dialogContent.scrollTop = 0;
      }
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log('The dialog was closed');
    });
  }
}
