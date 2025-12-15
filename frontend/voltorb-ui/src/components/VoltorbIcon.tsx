export default function VoltorbIcon() {
  return (
    <div style={{
      width: 36,
      height: 36,
      borderRadius: "50%",
      background: "linear-gradient(#fff 50%, #e53935 50%)",
      border: "2px solid black",
      position: "relative"
    }}>
      <div style={{
        position: "absolute",
        top: "50%",
        left: 0,
        right: 0,
        height: 2,
        background: "black"
      }} />
      <div style={{
        position: "absolute",
        top: "45%",
        left: "45%",
        width: 6,
        height: 6,
        borderRadius: "50%",
        background: "black"
      }} />
    </div>
  );
}
