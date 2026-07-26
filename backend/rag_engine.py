import os
import glob
import sqlite3
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUALS_DIR = os.path.join(BASE_DIR, 'data', 'manuals')
DB_PATH = os.path.join(BASE_DIR, 'factory_maintenance.db')

class RAGMaintenanceAssistant:
    def __init__(self):
        self.manual_documents = []
        self.load_manuals()

    def load_manuals(self):
        """Load markdown manuals into memory chunks."""
        self.manual_documents = []
        if os.path.exists(MANUALS_DIR):
            manual_files = glob.glob(os.path.join(MANUALS_DIR, '*.md'))
            for filepath in manual_files:
                doc_name = os.path.basename(filepath)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Split manual into sections by headers
                    sections = re.split(r'\n(?=##?\s)', content)
                    for sec in sections:
                        if sec.strip():
                            self.manual_documents.append({
                                'file': doc_name,
                                'text': sec.strip()
                            })

    def search_manuals(self, query, top_k=3):
        """Rank manual sections based on term overlap."""
        query_terms = set(re.findall(r'\w+', query.lower()))
        scored_docs = []
        for doc in self.manual_documents:
            doc_terms = set(re.findall(r'\w+', doc['text'].lower()))
            overlap = len(query_terms.intersection(doc_terms))
            if overlap > 0:
                scored_docs.append((overlap, doc))
        
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

    def query_database(self, query):
        """Query SQLite database for equipment history or maintenance logs."""
        if not os.path.exists(DB_PATH):
            return None

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Identify machine IDs in query (e.g. M-101, M-102, Machine 101, 101, 102, M101, M-201, M-202, M-301)
        machine_match = re.search(r'm[-_\s]?(\d{3})|machine\s*(\d{3})|101|102|201|202|301', query, re.IGNORECASE)
        m_id = None
        if machine_match:
            digits = next(g for g in machine_match.groups() if g is not None)
            m_id = f"M-{digits}"

        db_results = []
        if m_id:
            cursor.execute('''
                SELECT f.event_id, f.downtime_hours, f.defect_flag, f.maintenance_cost_usd, 
                       f.maintenance_type, f.description, d.date_str, e.name as machine_name, e.type as machine_type,
                       t.name as tech_name
                FROM fact_maintenance_events f
                JOIN dim_date d ON f.date_id = d.date_id
                JOIN dim_equipment e ON f.equipment_id = e.equipment_id
                JOIN dim_technician t ON f.technician_id = t.technician_id
                WHERE f.equipment_id = ?
                ORDER BY d.date_str DESC
            ''', (m_id,))
            db_results = [dict(row) for row in cursor.fetchall()]

        # General summary if no specific machine ID was found
        if not db_results and ("history" in query.lower() or "recent" in query.lower() or "downtime" in query.lower() or "log" in query.lower()):
            cursor.execute('''
                SELECT f.event_id, f.equipment_id, f.downtime_hours, f.maintenance_cost_usd,
                       f.maintenance_type, f.description, d.date_str, e.name as machine_name
                FROM fact_maintenance_events f
                JOIN dim_date d ON f.date_id = d.date_id
                JOIN dim_equipment e ON f.equipment_id = e.equipment_id
                ORDER BY d.date_str DESC LIMIT 5
            ''')
            db_results = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return {'machine_id': m_id, 'events': db_results}

    def answer_question(self, question):
        """Generate RAG synthesized response."""
        relevant_manuals = self.search_manuals(question)
        db_data = self.query_database(question)

        response_parts = []
        sources_used = []

        # 1. Include Database Record Answer if relevant
        if db_data and db_data['events']:
            m_id = db_data['machine_id']
            events = db_data['events']
            sources_used.append(f"SQL Data Warehouse (fact_maintenance_events for {m_id if m_id else 'All Equipment'})")
            
            response_parts.append(f"### 📊 Equipment History & Database Records")
            if m_id:
                latest = events[0]
                response_parts.append(f"**Equipment**: `{m_id}` ({latest['machine_name']})")
                response_parts.append(f"**Last Serviced Date**: **{latest['date_str']}**")
                response_parts.append(f"**Maintenance Type**: `{latest['maintenance_type']}`")
                response_parts.append(f"**Technician**: {latest['tech_name']}")
                response_parts.append(f"**Downtime Duration**: {latest['downtime_hours']} hrs | **Cost**: ${latest['maintenance_cost_usd']:,.2f}")
                response_parts.append(f"**Action Taken**: {latest['description']}")

                if len(events) > 1:
                    response_parts.append("\n**Previous Historical Maintenance Events**:")
                    for ev in events[1:]:
                        response_parts.append(f"- **{ev['date_str']}** (`{ev['maintenance_type']}`): {ev['description']} ({ev['downtime_hours']}h downtime)")
            else:
                response_parts.append("**Recent Factory Maintenance Events**:")
                for ev in events:
                    response_parts.append(f"- **{ev['date_str']}** | `{ev['equipment_id']}` ({ev['machine_name']}): {ev['description']}")

        # 2. Include Equipment Manual Procedure Answer if relevant
        if relevant_manuals:
            response_parts.append("\n### 📖 Technical Equipment Manual Instructions")
            for doc in relevant_manuals:
                sources_used.append(f"Manual Document (`{doc['file']}`)")
                response_parts.append(f"**Source Document**: `{doc['file']}`\n")
                response_parts.append(doc['text'])
                response_parts.append("\n---")

        if not response_parts:
            return {
                "answer": f"I analyzed our Smart Factory Knowledge Base (Database & Technical Manuals), but couldn't find a direct match for: *\"{question}\"*.\n\nTry asking queries like:\n- *\"When was Machine 101 or Machine 102 last serviced?\"*\n- *\"What is the procedure for high bearing vibration in motor M-201?\"*\n- *\"What is the maintenance procedure for transformer temperature spike?\"*",
                "sources": []
            }

        final_answer = "\n\n".join(response_parts)
        return {
            "answer": final_answer,
            "sources": list(set(sources_used))
        }

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    assistant = RAGMaintenanceAssistant()
    res = assistant.answer_question("When was Machine 102 last serviced?")
    print("ANSWER:\n", res['answer'])
    print("\nSOURCES:", res['sources'])
