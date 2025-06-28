import { ApplicationConfig, provideZoneChangeDetection, importProvidersFrom } from '@angular/core';
// provideBrowserGlobalErrorListeners seems to be removed or changed in latest versions,
// if you encounter errors related to it, it might need adjustment based on specific Angular version.
// For now, we'll keep it if your ng new command included it.
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
// If provideBrowserGlobalErrorListeners was part of your initial setup, and you need it:
// import { provideBrowserGlobalErrorListeners } from '@angular/core';


export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    // If you had provideBrowserGlobalErrorListeners() and need it, add it back here.
    // e.g., provideBrowserGlobalErrorListeners(),
    importProvidersFrom(HttpClientModule),
    importProvidersFrom(BrowserAnimationsModule) // Required for Angular Material animations
  ]
};
