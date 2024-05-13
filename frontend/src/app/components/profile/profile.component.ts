import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder } from '@angular/forms';
import { HotToastService } from '@ngneat/hot-toast';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { switchMap, tap } from 'rxjs';
import { ProfileUser } from 'src/app/models/user';
import { ImageUploadService } from 'src/app/services/image-upload.service';
// import { UsersService } from 'src/app/services/users.service';
import { AuthService } from 'src/app/services/auth.service';

@UntilDestroy()
@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
})
export class ProfileComponent implements OnInit {
  user$ = this.authService.currentUser$;

  profileForm = this.fb.group({
    uid: [''],
    displayName: [''],
    firstName: [''],
    lastName: [''],
    phone: [''],
    address: [''],
    age: [''],
    weight: [''],
  });

  constructor(
    private imageUploadService: ImageUploadService,
    private toast: HotToastService,
    // private usersService: UsersService,
    private fb: NonNullableFormBuilder,
    private authService: AuthService
  ) {
    console.log(this.user$);
  }

  ngOnInit(): void {
    this.authService.currentUser$.subscribe((user) => {
      if (user) {
        console.log('User is logged in', user);
      } else {
        console.log('No user is logged in');
      }
    });
  }

  uploadFile(event: any) {
    console.log(event);
    // this.imageUploadService
    //   .uploadImage(event.target.files[0], `images/profile/${uid}`)
    //   .pipe(
    //     this.toast.observe({
    //       loading: 'Uploading profile image...',
    //       success: 'Image uploaded successfully',
    //       error: 'There was an error in uploading the image',
    //     }),
    // switchMap((photoURL) =>
    //   this.usersService.updateUser({
    //     uid,
    //     photoURL,
    //   })
    // )
    // )
    // .subscribe();
  }

  saveProfile() {
    const { uid, ...data } = this.profileForm.value;

    if (!uid) {
      return;
    }

    // this.usersService
    //   .updateUser({ uid, ...data })
    //   .pipe(
    //     this.toast.observe({
    //       loading: 'Saving profile data...',
    //       success: 'Profile updated successfully',
    //       error: 'There was an error in updating the profile',
    //     })
    //   )
    //   .subscribe();
  }
}
