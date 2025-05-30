export const Label = ({ htmlFor, children }) => (
  <label htmlFor={htmlFor} className="block font-semibold mb-1">
    {children}
  </label>
);
