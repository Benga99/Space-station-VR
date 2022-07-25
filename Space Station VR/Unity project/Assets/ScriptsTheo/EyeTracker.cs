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

    Dictionary<string, float> objectsTracked = new Dictionary<string, float>();
    Dictionary<string, string> helpers = new Dictionary<string, string>();


    List<Vector3> playerPositions = new List<Vector3>();

    float time = 0;
    float totalTimePassed = 0;

    string filepathEYE;
    string filepathPOS;
    string filepathHIN;

    private void Start()
    {
        helperCard = FindObjectOfType<HelperCard>();
        filepathEYE = path + day + "eyee" + participantID + "-" + roomID + ".csv";
        filepathPOS = path + day + "posit" + participantID + "-" + roomID + ".csv";
        filepathHIN = path + day + "hints" + participantID + "-" + roomID + ".csv";
        if (File.Exists(filepathEYE) || File.Exists(filepathPOS) || File.Exists(filepathHIN))
        {
            Debug.LogError("Participant log files already exists ID " + participantID + "-" + roomID);
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
                Application.Quit();
#endif
        }
    }

    // Update is called once per frame
    void Update()
    {
        ray = Camera.main.ViewportPointToRay(new Vector3(0.5F, 0.5F, 0));
        
        if (Physics.Raycast(ray, out hit, Mathf.Infinity))
        {
            if(hit.transform.gameObject.tag != "Wall" && hit.transform.gameObject.name != null && hit.transform.gameObject.name.Length > 0)
            {
                if (objectsTracked.ContainsKey(hit.transform.gameObject.name))
                {
                    objectsTracked[hit.transform.gameObject.name] += Time.deltaTime;
                }
                else
                {
                    objectsTracked[hit.transform.gameObject.name] = Time.deltaTime;
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


        

        String csv2 = String.Join(Environment.NewLine, playerPositions.Select(d => $"{d.ToString()}"));
        String csv3 = String.Join(Environment.NewLine, helpers.Select(d => $"{d.Key};{d.Value}"));
        String csv = String.Join(Environment.NewLine, objectsTracked.Select(d => $"{d.Key};{(int)d.Value};{" seconds"}"));

        if (!Directory.Exists(path + day))
        {
            Directory.CreateDirectory(path + day);
        }

        if (File.Exists(filepathEYE) || File.Exists(filepathPOS) || File.Exists(filepathHIN))
        {

        }
        else
        {
            File.WriteAllText(filepathPOS, csv2);
            File.WriteAllText(filepathHIN, csv3);
            File.WriteAllText(filepathEYE, csv);
        }
        //OpenAllEyeTracking();
    }

    private void OpenAllEyeTracking()
    {
        Dictionary<string, float> allTracking = new Dictionary<string, float>();

        for (int pid = 1; pid <= 5; pid++)
        {
            for(int rid = 3; rid <= 3; rid++)
            {
                using (var reader = new StreamReader($"./EyeTrackingData/Test/eyee{pid}-{rid}.csv"))
                {
                    while (!reader.EndOfStream)
                    {
                        var line = reader.ReadLine();
                        var spl = line.Split(';');

                        if (allTracking.ContainsKey(spl[0]))
                        {
                            allTracking[spl[0]] += int.Parse(spl[1]);
                        }
                        else
                        {
                            allTracking[spl[0]] = int.Parse(spl[1]);
                        }
                    }
                }
            }
        }

        String csv4 = String.Join(Environment.NewLine, allTracking.Select(d => $"{d.Key};{(int)d.Value};{" seconds"}"));
        File.WriteAllText($"./EyeTrackingData/Test/finalEye.csv", csv4);

    }
}
