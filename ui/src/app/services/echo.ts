import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class Echo {
  private apiUrl = '/api/echo'; // Proxied by Nginx

  constructor(private http: HttpClient) { }

  sendEcho(message: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { message });
  }
}
