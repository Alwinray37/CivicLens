/**
 * Error message display component
 */
export default function ErrorMessage({ error }) {
    return (
        <div className="alert alert-danger" role="alert">
            <strong>An error occurred:</strong> {error?.message || 'Unknown error'}
        </div>
    );
}
