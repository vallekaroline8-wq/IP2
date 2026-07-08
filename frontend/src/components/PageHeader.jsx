import { Button } from "@/components/ui/button";
import { FileText, FileSpreadsheet } from "lucide-react";
import { downloadReport } from "@/utils/ui";

export const PageHeader = ({ title, subtitle, children, exportResource }) => (
  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 animate-fade-in">
    <div>
      <h1 className="font-heading text-2xl font-extrabold tracking-tight text-foreground" data-testid="page-title">{title}</h1>
      {subtitle && <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>}
    </div>
    <div className="flex items-center gap-2 flex-wrap">
      {exportResource && (
        <>
          <Button variant="outline" size="sm" onClick={() => downloadReport(exportResource, "pdf")} data-testid="export-pdf-btn">
            <FileText className="w-4 h-4 mr-1.5" /> PDF
          </Button>
          <Button variant="outline" size="sm" onClick={() => downloadReport(exportResource, "excel")} data-testid="export-excel-btn">
            <FileSpreadsheet className="w-4 h-4 mr-1.5" /> Excel
          </Button>
        </>
      )}
      {children}
    </div>
  </div>
);
