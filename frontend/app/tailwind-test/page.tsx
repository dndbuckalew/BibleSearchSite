export default function TailwindTest() {
  return (
    <>
      <div
        style={{
          width: "96px",
          height: "96px",
          backgroundColor: "yellow",
          border: "4px solid red",
          marginBottom: "24px",
        }}
      >
        Inline
      </div>

      <div className="w-24 h-24 bg-yellow-200 border-4 border-red-600">
        Tailwind
      </div>
    </>
  );
}
