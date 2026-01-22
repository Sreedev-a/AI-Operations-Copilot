import "./globals.css";import {Shell} from "@/components/Shell";
export const metadata={title:"AI Operations Copilot",description:"Agentic incident investigation and human-approved remediation"};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><Shell>{children}</Shell></body></html>}
