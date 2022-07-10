using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

public class EyeTracker : MonoBehaviour
{
    public int participantID;
    public int roomID;
    public string path;
    public string day;

    public GameObject HeadFollow;

    private HelperCard helperCard;

    RaycastHit hit;
    Ray ray;

    Dictionary<GameObject, float> objectsTracked = new Dictionary<GameObject, float>();
    Dictionary<string, string> helpers = new Dictionary<string, string>();


    List<Vector3> playerPositions = new List<Vector3>();

    float time = 0;
    float totalTimePassed = 0;


    private void Start()
    {
        helperCard = FindObjectOfType<HelperCard>();
    }

    // Update is called once per frame
    void Update()
    {
        ray = Camera.main.ViewportPointToRay(new Vector3(0.5F, 0.5F, 0));
        
        if (Physics.Raycast(ray, out hit, Mathf.Infinity))
        {
            if(hit.transform.gameObject.tag != "Wall")
            {
                if (objectsTracked.ContainsKey(hit.transform.gameObject))
                {
                    objectsTracked[hit.transform.gameObject] += Time.deltaTime;
                }
                else
                {
                    objectsTracked[hit.transform.gameObject] = Time.deltaTime;
                }
            }
        }


        if(time > 0.1f)
        {
            playerPositions.Add(HeadFollow.transform.position);
            time = 0;
        }

        time += Time.deltaTime;
        totalTimePassed += Time.deltaTime;
    }

    private void OnApplicationQuit()
    {
        helpers.Add("hint1 used", helperCard.showCard1.ToString());
        helpers.Add("hint2 used", helperCard.showCard2.ToString());
        helpers.Add("hint3 used", helperCard.showCard3.ToString());
        helpers.Add("total time passed", $"{(int)(totalTimePassed / 60)}:{((int)(totalTimePassed % 60)).ToString("00")} minutes" );


        String csv = String.Join(Environment.NewLine, objectsTracked.Select(d => $"{d.Key.ToString().Substring(0, d.Key.ToString().Length - 24)};{(int)d.Value};{" seconds"}"));
        String csv2 = String.Join(Environment.NewLine, playerPositions.Select(d => $"{d.ToString()}"));
        String csv3 = String.Join(Environment.NewLine, helpers.Select(d => $"{d.Key};{d.Value}"));

        if (!Directory.Exists(path + day))
        {
            Directory.CreateDirectory(path + day);
        }

        string filepathEYE = path + day + "eyee" + participantID + "-" + roomID + ".csv";
        string filepathPOS = path + day + "posit" + participantID + "-" + roomID + ".csv";
        string filepathHIN = path + day + "hints" + participantID + "-" + roomID + ".csv";

        if (File.Exists(filepathEYE) || File.Exists(filepathPOS) || File.Exists(filepathHIN))
        {
            Debug.LogError("Participant log files already exists ID " + participantID + "-" + roomID);
            UnityEditor.EditorApplication.isPlaying = false;
        }
        else
        {
            File.WriteAllText(filepathEYE, csv);
            File.WriteAllText(filepathPOS, csv2);
            File.WriteAllText(filepathHIN, csv3);
        }
    }
}
