export default function ErrorMessage({ message }) {
  return (
    <div
      style={{
        background: "#ffe0e0",
        color: "#900",
        padding: "12px",
        borderRadius: "8px",
        marginTop: "15px",
        border: "1px solid #ffb3b3",
        fontSize: "14px"
      }}
    >
      ❗ {message}
    </div>
  );
}
