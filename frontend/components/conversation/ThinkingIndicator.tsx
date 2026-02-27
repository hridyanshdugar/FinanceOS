export function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-card border border-border rounded-2xl rounded-bl-md px-5 py-4">
        <p className="text-[11px] font-medium text-primary mb-2">Shadow</p>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot" />
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot-delay-1" />
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot-delay-2" />
        </div>
      </div>
    </div>
  );
}
