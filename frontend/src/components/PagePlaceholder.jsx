export default function PagePlaceholder({ title, description }) {
  return (
    <section className="page-card">
      <p className="eyebrow">Frontend foundation</p>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}
