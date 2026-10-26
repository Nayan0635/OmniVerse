"""
List every file ingested into database + its chunk count.
Run:  python show_files.py. it isn't connected with anyone.
"""
from core import vector_store

def main():
    sources = vector_store.all_sources()
    if not sources:
        print("📭 No files ingested yet. Run 'python _ingest.py' first.")
        return

    print(f"\n📁 ChromaDB collection '{vector_store.get_collection().name}'")
    print("-" * 55)
    total = 0
    for name, count in sorted(sources.items()):
        print(f"   {name:<35} → {count:>3} chunks")
        total += count
    print("-" * 55)
    print(f"   {len(sources)} files, {total} total chunks\n")


if __name__ == "__main__":
    main()