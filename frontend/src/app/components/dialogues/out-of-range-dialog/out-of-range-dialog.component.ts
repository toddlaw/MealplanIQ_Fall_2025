import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

/**
 * Component for displaying a dialog when the user enters a value outside the allowed range.
 * This dialog shows a list of messages indicating the issues with the input.
 * @author BCIT May 2025
 */
@Component({
  selector: 'app-out-of-range-dialog',                  // component selector
  templateUrl: './out-of-range-dialog.component.html',  // template file path
  styleUrls: ['./out-of-range-dialog.component.css']    // optional style file path
})
export class OutOfRangeDialogComponent {
  // Injects dialog reference and incoming messages data when dialog is opened
  constructor(
    public dialogRef: MatDialogRef<OutOfRangeDialogComponent>,  // reference to dialog instance
    @Inject(MAT_DIALOG_DATA) public messages: string[]          // array of messages passed from parent
  ) {}

  // Method to close the dialog window when close button is clicked
  closeDialog(): void {
    this.dialogRef.close();
  }
}
