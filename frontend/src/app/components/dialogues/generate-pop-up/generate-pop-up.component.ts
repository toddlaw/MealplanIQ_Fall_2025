import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-generate-pop-up',
  templateUrl: './generate-pop-up.component.html',
  styleUrls: ['./generate-pop-up.component.css'],
})
export class GeneratePopUpComponent {
  title: string;
  confirmLabel: string;

  constructor(
    public dialogRef: MatDialogRef<GeneratePopUpComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.title = data.title;
    this.confirmLabel = data.confirmLabel;
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onLogin(): void {
    this.dialogRef.close(true);
  }
}
