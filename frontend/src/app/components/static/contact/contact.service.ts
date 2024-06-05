import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  private apiUrl = 'https://mealplaniq-may-2024.uw.r.appspot.com/send-email'; // replace with the actual backend api

  constructor(private http: HttpClient) { }

  sendEmail(formData: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, formData);
  }
}
