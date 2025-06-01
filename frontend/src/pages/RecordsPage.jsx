import React, { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { BASE_API_URL } from "../utils/apiConfig"; // <--- ADD THIS LINE!
// Ensure this path is correct relative to this file.

const RecordsPage = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedEncounterId, setSelectedEncounterId] = useState(null); // You'll need a way to set this
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredRecords, setFilteredRecords] = useState([]);

  useEffect(() => {
    const fetchRecords = async () => {
      if (!selectedEncounterId) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setError("");
      try {
        const response = await axios.get(
          `${BASE_API_URL}/encounters/${selectedEncounterId}/records` // <--- UPDATED URL HERE!
        );
        setRecords(response.data);
      } catch (err) {
        setError("Failed to fetch records.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecords();
  }, [selectedEncounterId]);

  useEffect(() => {
    const filterRecords = () => {
      const lowerSearchTerm = searchTerm.toLowerCase();
      const results = records.filter(
        (record) =>
          record.details.toLowerCase().includes(lowerSearchTerm) ||
          record.record_date.toLowerCase().includes(lowerSearchTerm) ||
          String(record.record_id).includes(lowerSearchTerm)
      );
      setFilteredRecords(results);
    };

    filterRecords();
  }, [searchTerm, records]);

  // Placeholder for selecting an encounter - you'll need to implement this UI
  const handleEncounterSelect = (encounterId) => {
    setSelectedEncounterId(encounterId);
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Health Records</h1>

      {/* Placeholder for encounter selection */}
      {/* You'll need to uncomment and implement a way to set `selectedEncounterId`
          For example, from a dropdown of available encounters or via URL params. */}
      {/* <div className="mb-4">
        <Label htmlFor="encounterId">Select Encounter ID:</Label>
        <Input
          type="number"
          id="encounterId"
          value={selectedEncounterId || ""}
          onChange={(e) => setSelectedEncounterId(e.target.value)}
        />
        <Button onClick={() => handleEncounterSelect(parseInt(selectedEncounterId))}>
          Load Records
        </Button>
      </div> */}

      <div className="mb-4 flex items-center space-x-2">
        <Label htmlFor="search">Search Records:</Label>
        <Input
          type="text"
          id="search"
          placeholder="Search by details, date, or ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {loading && <p>Loading records...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {filteredRecords.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecords.map((record) => (
            <Card key={record.record_id} className="shadow-md">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">
                  Record ID: {record.record_id}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-2">
                  Date: {record.record_date}
                </CardDescription>
                <CardDescription className="text-sm text-gray-600">
                  Details: {record.details.substring(0, 100)}...
                </CardDescription>
                {/* Add buttons for viewing details, editing, deleting */}
                {/* <Button size="sm" className="mt-2">View Details</Button> */}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {filteredRecords.length === 0 &&
        !loading &&
        !error &&
        records.length > 0 && (
          <p>No records found matching your search term.</p>
        )}

      {records.length === 0 && !loading && !error && !selectedEncounterId && (
        <p>No encounter selected to display records.</p>
      )}

      {records.length === 0 && !loading && !error && selectedEncounterId && (
        <p>No records found for the selected encounter.</p>
      )}

      {/* Button to add a new record - you might want a separate form/page for this */}
      {selectedEncounterId && <Button className="mt-6">Add New Record</Button>}
    </div>
  );
};

export default RecordsPage;
