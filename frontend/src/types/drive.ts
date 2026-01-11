export interface DriveItem {
  id: string;
  name: string;
  mimeType: string;
  webViewLink?: string;
}

export interface Breadcrumb {
  id: string | null;
  name: string;
}
