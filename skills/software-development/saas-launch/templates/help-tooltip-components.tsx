// HelpIcon - Click-to-reveal tooltip for form fields
// Usage: wrap next to any <label> text
//
// <label>
//   Field Name
//   <HelpIcon help="Explanation text" tip="💡 Tip text" />
// </label>

function HelpIcon({ help, tip }: { help: string; tip?: string }) {
  const [open, setOpen] = useState(false);

  return (
    <span className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        className="inline-flex items-center justify-center w-4 h-4 ml-1 text-gray-400 hover:text-blue-500 focus:outline-none transition-colors"
        aria-label="Help"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.529 9.988a2.502 2.502 0 115.191.237C14.43 12.45 12.5 13.5 12.5 15m0 2.5h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
      {open && (
        <div className="absolute z-50 left-1/2 -translate-x-1/2 bottom-full mb-2 w-72 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl">
          <p className="leading-relaxed">{help}</p>
          {tip && <p className="mt-2 text-blue-300 leading-relaxed">{tip}</p>}
          <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
        </div>
      )}
    </span>
  );
}

// NotSureBanner - Shows preset cards with descriptions for users who don't know what inputs to use
// Usage: place above the form input grid

function NotSureBanner({ onApply }: { onApply: (presetKey: string) => void }) {
  const [show, setShow] = useState(false);

  return (
    <div className="mb-2">
      <button
        type="button"
        onClick={() => setShow(!show)}
        className="text-xs text-blue-600 hover:text-blue-800 hover:underline font-medium flex items-center gap-1"
      >
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Not sure what to put? Try a preset
      </button>
      {show && (
        <div className="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900 font-medium mb-3">Pick a preset to auto-fill realistic values:</p>
          <div className="flex flex-wrap gap-2">
            {presets.map(({ key, label, desc }) => (
              <button
                key={key}
                onClick={() => { onApply(key); setShow(false); }}
                className="flex-1 min-w-[160px] p-3 bg-white rounded-lg border border-blue-200 hover:border-blue-400 hover:shadow-sm transition-all text-left"
              >
                <p className="text-sm font-medium text-gray-900">{label}</p>
                <p className="text-xs text-gray-500 mt-1">{desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// FieldConfig with lifeLabel - Reframe technical fields as lifestyle questions
// Example config entry:
// {
//   key: "desiredAnnualIncome",
//   label: "Target Annual Income",
//   suffix: "/yr",
//   lifeLabel: "How much do you want to earn per year to live your ideal life?",
//   help: "Think about the life you want — not just survival.",
//   tip: "💡 $60K = comfortable, $100K = lifestyle freedom",
// }
