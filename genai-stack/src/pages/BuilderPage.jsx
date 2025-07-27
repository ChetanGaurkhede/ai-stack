import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PlusCircle, ExternalLink, Loader, Trash } from "lucide-react";
import CreateStack from "../components/CreateStack";
import { useStackData } from "../context/stackAiContext";
import axios from "axios";

const MyStacksPage = () => {
  const navigate = useNavigate();

  const { stacks, setStacks, updateStack, loading, setLoading } =
    useStackData();
  const [workflows, setWorkflows] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  const handleCreateStack = (newStack) => {
    const id = Date.now().toString(); // mock id
    setStacks([...stacks, { id, ...newStack }]);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        "http://localhost:8000/api/v1/workflows/"
      );
      setStacks(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch workflows:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []); // ← run only once on mount

  const handleEdit = (stackId) => {
    const currentStack = stacks.find((stack) => stack.id === stackId);
    if (currentStack) {
      updateStack(currentStack);
      navigate(`/builder/${stackId}`);
    } else {
      console.warn(`Stack with ID ${stackId} not found`);
    }
  };

  if (loading) {
    return (
      <div className="w-full h-screen flex justify-center items-center">
        <Loader className="animate-spin h-5 w-5" />
      </div>
    );
  }
  const confirmDelete = async () => {
    try {
      await axios.delete(
        `http://localhost:8000/api/v1/workflows/${confirmDeleteId}`
      );
      setStacks((prev) => prev.filter((stack) => stack.id !== confirmDeleteId));
      setConfirmDeleteId(null); // close modal
    } catch (error) {
      console.error("❌ Failed to delete workflow:", error);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-white p-8 pt-22">
        <div className="flex items-center justify-between mb-6 pb-3 max-6xl mx-auto border-b border-gray-300">
          <h1 className="text-2xl font-semibold">My Stacks</h1>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl shadow cursor-pointer"
          >
            <PlusCircle size={18} />
            New Stack
          </button>
        </div>

        {stacks.length === 0 ? (
          <div className="flex justify-center items-center h-[60vh] ">
            <div className=" border border-gray-200 p-8 py-5 rounded-2xl shadow-sm max-w-md">
              <h2 className="text-xl font-medium mb-2">Create New Stack</h2>
              <p className="text-gray-500 mb-4">
                Start building your generative AI apps with our essential tools
                and frameworks.
              </p>
              <button
                onClick={() => setShowModal(true)}
                className="bg-green-600 hover:bg-green-700 cursor-pointer text-white px-4 py-2 rounded-xl flex gap-2 items-center"
              >
                <PlusCircle size={18} />
                New Stack
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stacks.map((stack) => (
              <div
                key={stack.id}
                className="border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition relative"
              >
                <h3 className="font-semibold text-lg mb-1">{stack.name}</h3>
                <p className="text-gray-500 text-sm mb-3">
                  {stack.description}
                </p>
                <button
                  onClick={() => handleEdit(stack.id)}
                  className="flex items-center gap-1 text-sm border px-3 py-1 rounded hover:bg-gray-100"
                >
                  Edit Stack <ExternalLink size={14} />
                </button>
                <div className="absolute right-2 top-2 cursor-pointer bg-gray-200 p-2 rounded-lg shadow-2xl">
                  <Trash
                    onClick={() => setConfirmDeleteId(stack.id)}
                    className=" text-red-500 h-3 w-3"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {confirmDeleteId && (
        <div className="fixed inset-0 z-50 bg-[#000000ca] backdrop-blur-sm flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-lg w-[320px]">
            <h3 className="text-lg font-semibold mb-3">Confirm Deletion</h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to delete this stack? This action cannot be
              undone.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setConfirmDeleteId(null)}
                className="px-4 py-2 text-sm border rounded text-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <CreateStack
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreate={handleCreateStack}
      />
    </>
  );
};

export default MyStacksPage;
