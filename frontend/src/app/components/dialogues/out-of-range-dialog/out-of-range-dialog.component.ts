import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-out-of-range-dialog',
  templateUrl: './out-of-range-dialog.component.html',
  styleUrls: ['./out-of-range-dialog.component.css']
})
export class OutOfRangeDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<OutOfRangeDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public messages: string[]
  ) {}

  closeDialog(): void {
    this.dialogRef.close();
  }
}
